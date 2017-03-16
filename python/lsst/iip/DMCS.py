import toolsmod
from toolsmod import get_timestamp
import logging
import pika
import redis
import yaml
import sys, traceback
import os
import time
from time import sleep
import thread
from const import *
from Scoreboard import Scoreboard
from JobScoreboard import JobScoreboard
from AckScoreboard import AckScoreboard
from StateScoreboard import StateScoreboard
from BacklogScoreboard import BacklogScoreboard
from Consumer import Consumer
from SimplePublisher import SimplePublisher

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class DMCS:
    """As this set of consumer callbacks cannot block for the lengthy time some tasks (such as readouts)
       will take, a thread must poll for acks and handle accordingly. Tasks will be issued, and
       then a cyclical thread will read through acks and update scoreboards accordingly.

       Another thing that must happen here, is that state should be tracked in a hash specific to each
       device, each 'last state' must be pushed on to the RHS of a list structure for that particular
       commandable device. 
    """

    JOB_SCBD = None
    ACK_SCBD = None
    STATE_SCBD = None
    BACKLOG_SCBD = None
    OCS_BDG_PUBLISH = "ocs_bdg_publish"  #Messages from OCS Bridge
    OCS_BDG_CONSUME = "ocs_bdg_consume"  #Messages to OCS Bridge
    DMCS_PUBLISH = "dmcs_publish" #Used for Foreman comm
    DMCS_CONSUME = "dmcs_consume" #Used for Foreman comm
    #AR_FOREMAN_ACK_PUBLISH = "ar_foreman_ack_publish" #Used for Foreman comm
    AR_FOREMAN_ACK_PUBLISH = "dmcs_ack_consume" #Used for Foreman comm
    ACK_PUBLISH = "ack_publish"
    OCS_BDG_PUBLISH = "ocs_dmcs_consume"
    CCD_LIST = [] 


    def __init__(self, filename=None):
        toolsmod.singleton(self)
        LOGGER.info('DMCS Init beginning')

        self._default_cfg_file = 'L1SystemCfg.yaml'
        if filename == None:
            filename = self._default_cfg_file


        LOGGER.info('Reading YAML Config file %s' % filename)
        try:
            cdm = toolsmod.intake_yaml_file(filename)
        except IOError, e:
            trace = traceback.print_exc()
            emsg = "Unable to find CFG Yaml file %s\n" % filename
            LOGGER.critical(emsg + trace)
            self.enter_fault_state(emsg)
            sys.exit(101) 

        LOGGER.info('Extracting values from Config dictionary')
        try:
            self._msg_name = cdm[ROOT][DMCS_BROKER_NAME]      # Message broker user & passwd
            self._msg_passwd = cdm[ROOT][DMCS_BROKER_PASSWD]   
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            ddict = cdm[ROOT]['FOREMAN_CONSUME_QUEUES']
            state_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_STATE_SCBD']
            job_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_JOB_SCBD']
            ack_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_ACK_SCBD']
            backlog_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_BACKLOG_SCBD']
            self.CCD_LIST = cdm[ROOT]['CCD_LIST']
            broker_vhost = cdm[ROOT]['BROKER_VHOST']
            queue_purges = cdm[ROOT]['QUEUE_PURGES']
        except KeyError, e:
            trace = traceback.print_exc()
            emsg = "Unable to find key in CDM representation of %s\n" % filename
            LOGGER.critical(emsg + trace)
            self.enter_fault_state(emsg)
            sys.exit(102) 

        ### FIXME Add a Sudo capability to run purges in rabbitmqctl
        #self.purge_broker(broker_vhost, queue_purges)
        self._base_broker_url = 'amqp_url'
        self._next_timed_ack_id = 0

        # TEMPORARY ONLY - Will be removed when config key nature is finalized
        # Build ccd_list as if a config key is being used... range val is numbee of CCDs to handle
        for i in range (1, 21):
            self.CCD_LIST


        LOGGER.info('Setting up DMCS Scoreboards')
        self.JOB_SCBD = JobScoreboard(job_db_instance)
        self.BACKLOG_SCBD = BacklogScoreboard(backlog_db_instance)
        self.ACK_SCBD = AckScoreboard(ack_db_instance)
        self.STATE_SCBD = StateScoreboard(state_db_instance, ddict)

        # Messages from OCS Bridge
        self._OCS_msg_actions = { OFFLINE: self.process_offline_command,
                              STANDBY: self.process_standby_command,
                              DISABLE: self.process_disable_command,
                              ENABLE: self.process_enable_command,
                              FAULT: self.process_fault_command,
                              FINAL: self.process_final_command,
                              NEXT_VISIT: self.process_next_visit_event,
                              START_INTEGRATION: self.process_start_integration_event,
                              READOUT: self.process_readout_event,
                              TELEMETRY: self.process_telemetry }

        self._foreman_msg_actions = { 'FOREMAN_HEALTH_ACK': self.process_ack,
                              'NEW_SESSION_ACK': self.process_ack,
                              'AR_NEXT_VISIT_ACK': self.process_ack,
                              'AR_START_INTEGRATION_ACK': self.process_ack,
                              'AR_READOUT_ACK': self.process_readout_results_ack,
                              'NEW_JOB_ACK': self.process_ack }


        self._base_broker_url = "amqp://" + self._msg_name + ":" + \
                                            self._msg_passwd + "@" + \
                                            str(self._base_broker_addr)
        LOGGER.info('Building _base_broker_url. Result is %s', self._base_broker_url)

        LOGGER.info('DMCS consumer setup')
        self.setup_consumers()

        LOGGER.info('DMCS publisher setup')
        self.setup_publishers()


        LOGGER.info('DMCS Init complete')



    def setup_consumers(self):
        LOGGER.info('Setting up consumers on %s', self._base_broker_url)
        LOGGER.info('Running start_new_thread on all DMCS consumer methods')

        self._ocs_bdg_consumer = Consumer(self._base_broker_url, self.OCS_BDG_PUBLISH, "YAML")
        try:
            thread.start_new_thread( self.run_ocs_bdg_consumer, ("thread-dmcs-consumer", 2,) )
        except Exception, e: # Catching naked exception as thread exceptions can be many
            trace = traceback.print_exc()
            emsg = "Unable to start new thread for OCS Bridge consumer"
            LOGGER.critical(emsg + trace)
            self.enter_fault_state(emsg)
            LOGGER.critical('Cannot start OCS Bridge consumer thread for DMCS, exiting...')
            print "Cannot start OCS Bridge consumer!"
            sys.exit(103)


        self._ack_consumer = Consumer(self._base_broker_url, self.AR_FOREMAN_ACK_PUBLISH, "YAML")
        try:
            thread.start_new_thread( self.run_ack_consumer, ("thread-ack-consumer", 2,) )
        except Exception, e:
            trace = traceback.print_exc()
            emsg = "Unable to start new thread for OCS Bridge consumer"
            LOGGER.critical(emsg + trace)
            self.enter_fault_state(emsg)
            LOGGER.critical('Cannot start ACK consumer thread for DMCS, exiting...')
            print "Cannot start ACK consumer for DMCS!"
            sys.exit(104)

        LOGGER.info('Finished starting all three consumer threads')


    def run_ocs_bdg_consumer(self, threadname, delay):
        LOGGER.debug('Thread ID in OCS Bridge consumer callback is %s', thread.get_ident())
        self._ocs_bdg_consumer.run(self.on_ocs_message)

    def run_ack_consumer(self, threadname, delay):
        LOGGER.debug('Thread ID in ACK consumer callback is %s', thread.get_ident())
        self._ack_consumer.run(self.on_ack_message)


    def setup_publishers(self):
        LOGGER.info('Setting up Base publisher on %s', self._base_broker_url)
        self._publisher = SimplePublisher(self._base_broker_url, YAML)



    def on_ocs_message(self, ch, method, properties, msg_dict):
        LOGGER.info('Processing message in OCS message callback')
        LOGGER.debug('Thread in OCS message callback of DMCS is %s', thread.get_ident())
        LOGGER.debug('Message from DMCS callback message body is: %s', str(msg_dict))

        handler = self._OCS_msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def on_ack_message(self, ch, method, properties, msg_dict):
        msg_dict = body 
        LOGGER.info('Processing message in ACK message callback')
        LOGGER.debug('Thread in ACK callback od DMCS is %s', thread.get_ident())
        LOGGER.debug('Message from ACK callback message body is: %s', str(msg_dict))

        handler = self._foreman_msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


   #==================================================================================== 
   # The following functions map to the state transition commands that the OCS will generate
   # It is noted here rather than in method documentation below (to keep descriptions simple),
   # that a FaultState is reachable from StandbyState, DisableState, and EnableState.


    def process_offline_command(self, msg):
        """Transition from StandbyState to OfflineState. Catch up work could conceivably 
           be done in OfflineState. There will be no contact with DDS, however. The only
           available transition is from OfflineState to Final...which is 'off.' 
           Any needed entities to be persisted beteen starts should happen after this transition. 
           The system cannot be brought back up to EnableState from OfflineState.

           When this method is called, DMCS should finish up any running jobs, and then 
           begin working on the backlog queue. If the backlog queue is empty, persist and shut down.

           Because the DDS is not reachable in the state resulting from this command, and 
           telemetry from tasks done on the TO-DO queue must be staged, and then sent when 
           the system returns to StandbyState.
        
        """
        new_state = "OFFLINE"
        device = msg['DEVICE']
        current_state = self.STATE_SCBD.get_device_state(device)

        # call transition check
        transition_check = self.validate_transition(current_state, new_state)

        if transition_check == True:
            self.send_ocs_ack(transition_check, str(device) + " device is now in " + new_state)
        else:
            response = "Invalid transition from " + str(current_state) + " to " + new_state
            response = response + ". Device remaining in " + current_state + " state."
            self.send_ocs_ack(transition_check, response)



    def process_standby_command(self, msg):
        """StandbyState is the initial system stste after the system comes up and makes connection with DDS.
           WHENEVER the StandbyState is entered, a new Session_ID is created. 
           IOW, the DMCS wakes up to find itself in StandbyState.
           Communication with DDS is expected and needed in ths state.
        """

        new_state = "STANDBY"
        device = msg['DEVICE']
        current_state = self.STATE_SCBD.get_device_state(device)

        # call transition check
        transition_check = self.validate_transition(current_state, new_state)

        if transition_check == True:
            self.send_ocs_ack(transition_check, str(device) + " device is now in " + new_state)
        else:
            response = "Invalid transition from " + str(current_state) + " to " + new_state
            response = response + ". Device remaining in " + current_state + " state."
            self.send_ocs_ack(transition_check, response)







        # send new session id to all
        session_id = self.STATE_SCBD.get_next_session_id()
        acks = self.send_new_session_msg(session_id)

        self.ack_timer(2)

        # Check ack response
        for a in acks:
            ack_responses = self.ACK_SCBD.get_components_for_timed_ack(a)

        ## XXX FIX  Do error trapping below
        ## acks is a List of ack_ids. The ack scoreboard is searched by the ack_id key
        ## Each ack_id will have a dict of components that acked under that ack_id
        ## These acks are set up as a different ack_id per device...is this necessary?
        ## under the [ack_id}, the under the component name[ar_foreman], there will be an ACK_BOOL.
        ## this tells whether the command was successful or not.
#        if ack_responses == None:
#            print "BIG Problem handling new session ack"
#
#            if ack_responses != None:
#                responses = ack_responses.keys()
#                for response in responses:
#                    if response['AR_FOREMAN'][ACK_BOOL] == False:
#                        # Mark this device as messed up...maybe enter fault.
#                        # This means component or device 'response' failed
#                        pass 
#            else:
#                #Enter a fault state, as no devices are responding
#                pass

        # Send return ack queue in new_session message


        # Set config key in state table
        # Send this state change to auditor
        # Ack back?



    def process_disable_command(self, msg):
        """Transition from EnableState to DisableState. Limited operation only is capable after 
           this transition; for example, transfer of 'catch up' work from camera buffer to archive 
           is possible, but no NextVisit events will be received while in this state.

        """
        new_state = "DISABLE"
        device = msg['DEVICE']
        current_state = self.STATE_SCBD.get_device_state(device)

        # call transition check
        transition_check = self.validate_transition(current_state, new_state)

        if transition_check == True:
            self.send_ocs_ack(transition_check, str(device) + " device is now in " + new_state)
        else:
            response = "Invalid transition from " + str(current_state) + " to " + new_state
            response = response + ". Device remaining in " + current_state + " state."
            self.send_ocs_ack(transition_check, response)



    def process_enable_command(self, msg):
        """Transition from DisableState to EnableState. Full operation is capable after this transition.

        """
        new_state = "ENABLE"
        device = msg['DEVICE']
        current_state = self.STATE_SCBD.get_device_state(device)

        # call transition check
        transition_check = self.validate_transition(current_state, new_state)

        if transition_check == True:
            self.send_ocs_ack(transition_check, str(device) + " device is now in " + new_state)
        else:
            response = "Invalid transition from " + str(current_state) + " to " + new_state
            response = response + ". Device remaining in " + current_state + " state."
            self.send_ocs_ack(transition_check, response)


    def process_fault_command(self):
        new_state = "FAULT"
        device = msg['DEVICE']
        current_state = self.STATE_SCBD.get_device_state(device)

        # call transition check
        transition_check = self.validate_transition(current_state, new_state)

        if transition_check == True:
            self.send_ocs_ack(transition_check, str(device) + " device is now in " + new_state)
        else:
            response = "Invalid transition from " + str(current_state) + " to " + new_state
            response = response + ". Device remaining in " + current_state + " state."
            self.send_ocs_ack(transition_check, response)



    def process_final_command(self):
        new_state = "FINAL"
        device = msg['DEVICE']
        current_state = self.STATE_SCBD.get_device_state(device)

        # call transition check
        transition_check = self.validate_transition(current_state, new_state)

        if transition_check == True:
            self.send_ocs_ack(transition_check, str(device) + " device is now in " + new_state)
        else:
            response = "Invalid transition from " + str(current_state) + " to " + new_state
            response = response + ". Device remaining in " + current_state + " state."
            self.send_ocs_ack(transition_check, response)



    def process_next_visit_event(self, params):
        # Send next visit info to any devices in enable state
        # Keep track of current Next Visit for each device.

        # First, get dict of devices in Enable state with their consume queues
        visit_id = params['VISIT_ID']
        self.JOB_SCBD.set_visit_id(visit_id)
        enabled_devices = self.STATE_SCBD.get_devices_by_state(ENABLE)

        acks = []
        for k in enabled_devices.keys():
            consume_queue = enabled_devices[k]
            ## FIXME - Must each enabled device use its own ack_id? Or
            ## can we use the same method for broadcasting Forwarder messages?  
            ack = self.get_next_timed_ack_id("NEXT_VISIT_ACK")
            acks.append(ack)
            msg = {}
            msg[MSG_TYPE] = NEXT_VISIT
            msg[ACK_ID] = ack
            msg[VISIT_ID] = params[VISIT_ID]
            msg[BORE_SIGHT] = params['BORE_SIGHT']
            msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
            self._publisher.publish_message(consume_queue, msg)

        self.ack_timer(2)
#        for a in acks:
#            ack_responses = self.ACK_SCBD.get_components_for_timed_ack(a)
#
#            if ack_responses != None:
#                responses = ack_responses.keys()
#                for response in responses:
#                    if response[ACK_BOOL] == False:
#                        # Mark this device as messed up...maybe enter fault.
#                        pass 
#            else:
#                #Enter a fault state, as no devices are responding
#                pass
            
            


    def process_start_integration_event(self, params):
        # Send start int message to all enabled devices, with details of job...include new job_num

        ## FIX - see temp hack below...
        ## CCD List will eventually be derived from config key. For now, using a list set in top of this class
        ccd_list = self.CCD_LIST
        visit_id = self.JOB_SCBD.get_current_visit()
        image_id = params[IMAGE_ID]
        job_num = self.STATE_SCBD.get_next_job_num( str(get_current_session_id()))
        self.JOB_SCBD.add_job(job_num, image_id, visit_id, ccd_list)
        self.JOB_SCBD.set_value_for_job(job_num, 'DEVICE', 'AR')

        ack_id = self.get_next_timed_ack_id("START_INT_ACK")

        msg_params = {}
        msg_params[MSG_TYPE] = 'START_INTEGRATION'
        msg_params[JOB_NUM] = job_num
        msg_params[SESSION_ID] = self.STATE_SCBD.get_current_session_id()
        msg_params[VISIT_ID] = self.JOB_SCBD.get_current_visit()
        msg_params[IMAGE_ID] = image_id
        msg_params['IMAGE_SRC'] = 'Blah'
        msg_params['RESPONSE_QUEUE'] = 'dmcs_ack_consume'
        msg_params[ACK_ID] = ack_id
        msg_params['CCD_LIST'] = ccd_list
        self._publisher.publish_message(self.STATE_SCBD.get_device_consume_queue(device), msg_params)
        self.JOB_SCBD.set_job_state(job_num, "DISPATCHED")

        self.ack_timer(3)
        ## XXX Don't check for responses right now...


####### # Right now, using only Archive...
#        enabled_devices = self.STATE_SCBD.get_devices_by_state(ENABLED)
#        ack_prefix = 
#        acks = {}
#        for k in enabled_devices.keys():
#            consume_queue = enabled_devices[k]
#            ack = self.get_next_timed_ack_id("NEXT_VISIT_ACK")
#            acks.append(ack)
#            self._publisher.publish_message(consume_queue, msg)



    #####################################################################
    # FIX How will this work? Will one readout event be sent, and then 
    #     all enabled devices respond? Or will a separate READOUT event
    #     be sent for each device? I am thinking the former - but this
    #     method only handles Archive readouts and must be modified
    #     to include Prompt Processing.
    #
    #     In addition, will the Start Integration message be device
    #     specific? How will job numbers be created and tracked?


 
    def process_readout_event(self, params):
        image_id = params['IMAGE_ID']
        device = params['DEVICE']

        ack_id = self.get_next_timed_ack_id("READOUT_ACK")

        msg_params = {}
        msg_params[MSG_TYPE] = 'READOUT'
        ## XXX Fix lime below and get rid of working line so device is simple passed in.
        #msg_params[JOB_NUM] = self.JOB_SCBD.get_open_job_num_for_device(device)
        msg_params[JOB_NUM] = self.JOB_SCBD.get_current_device_job(device)
        msg_params[SESSION_ID] = self.STATE_SCBD.get_current_session_id()
        msg_params[VISIT_ID] = self.JOB_SCBD.get_current_visit()
        msg_params[IMAGE_ID] = image_id
        msg_params['IMAGE_SRC'] = 'Blah'
        msg_params['RESPONSE_QUEUE'] = 'dmcs_ack_consume'
        msg_params[ACK_ID] = ack_id
        self._publisher.publish_message(self.STATE_SCBD.get_device_consume_queue(device), msg_params)
        # Update job scbd
        # add in two additional acks for format and transfer complete
        # Figure out how separate devices will be done using a device param in incoming msg
        # How will it know what job num to use???


    def process_telemetry(self, msg):
        pass


    def process_start_command(self):
        pass




    def process_offline_command(self):
        pass


    def process_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)


    def process_readout_results_ack(params):
        # FIXME make certain devices/job_nums are kept separate so OCS can be informed of results properly.
        job_num = params[JOB_NUM]
        results = params['RESULTS_LIST']

        # Mark job number done
        self.JOB_SCBD.set_job_state(job_num, "COMPLETE")

        # Store results for job with that job
        self.JOB_SCBD.set_results_for_job(job_num, results)

        failed_list = []
        keez = results.keys()
        for kee in keez:
            if (results[kee] == str(-1)) or (results[kee] == str(0)):
                failed_list.append(kee)

        # For each failed CCD, add CCD to Backlog Scoreboard
        if failed_list:
            self.BACKLOG_SCBD.add_ccds_by_job(job_num, failed_list, params)


    def get_backlog_stats(self):
        # return brief info on all backlog items.
        pass

    def get_backlog_details(self):
        # return detailed dictionary of all backlog items and the nature of each.
        pass

    def get_next_backlog_item(self):
        # This method will return a backlog item according to a policy in place.
        pass


    def send_new_session_msg(self, session_id):
        acks = [] 
        msg = {}
        msg['MSG_TYPE'] = 'NEW_SESSION'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['SESSION_ID'] = session_id

        ddict = self.STATE_SCBD.get_devices_by_state(None)
        for k in ddict.keys():
            consume_queue = ddict[k]
            ack_id = self.get_next_timed_ack_id("NEW_SESSION_ACK")
            msg['ACK_ID'] = ack_id
            acks.append(ack_id)
            self._publisher.publish_message(consume_queue, msg)

        return acks

    def validate_transition(self, current_state, new_state):
        current_index = toolsmod.state_enumeration[current_state]
        new_index = toolsmod.state_enumeration[new_state]
        transition_is_valid = toolsmod.state_matrix[current_index][new_index]
        return transition_is_valid
 


#    def get_next_timed_ack_id(self, ack_type):
#            self._publisher.publish_message(consume_queue, msg)
#
#        return acks
            
 


    def get_next_timed_ack_id(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        retval = ack_type + "_" + str(self._next_timed_ack_id).zfill(6)
        return retval 


    def ack_timer(self, seconds):
        sleep(seconds)
        return True

    def purge_broker(self, vhost, queues):
        for q in queues:
            cmd = "rabbitmqctl -p " + vhost + " purge_queue " + q
            os.system(cmd)

    def enter_fault_state(self, message):
        # tell other entities to enter fault state via messaging
        #  a. OCSBridge
        #  b. Foreman Devices
        #  c. Archive Controller
        #  d. Auditor
        # Raise an L1SystemError with message
        # Exit?
        pass


def main():
    logging.basicConfig(filename='logs/BaseForeman.log', level=logging.INFO, format=LOG_FORMAT)
    dmsc = DMCS()
    print "Beginning DMCS event loop..."
    try:
        while 1:
            # dmcs.get_next_backlog_item() ???
            pass
    except KeyboardInterrupt:
        pass

    print ""
    print "DMCS Done."


if __name__ == "__main__": main()
