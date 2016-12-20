import toolsmod
from toolsmod import get_timestamp
import logging
import pika
import redis
import yaml
import sys
import os
import time
from time import sleep
import thread
from const import *
from Scoreboard import Scoreboard
from JobScoreboard import JobScoreboard
from AckScoreboard import AckScoreboard
from StateScoreboard import StateScoreboard
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
    ENABLE = 'ENABLE'
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

        #self.purge_broker()
        self._default_cfg_file = 'ForemanCfg.yaml'
        if filename == None:
            filename = self._default_cfg_file

        cdm = toolsmod.intake_yaml_file(filename)

        try:
            self._base_name = cdm[ROOT][BASE_BROKER_NAME]      # Message broker user & passwd
            self._base_passwd = cdm[ROOT][BASE_BROKER_PASSWD]   
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            ddict = cdm[ROOT]['FOREMAN_CONSUME_QUEUES']
            state_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_STATE_SCBD']
            job_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_JOB_SCBD']
            ack_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_ACK_SCBD']
            backlog_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_BACKLOG_SCBD']
            self.CCD_LIST = cdm[ROOT]['CCD_LIST']
        except KeyError as e:
            print e
            print "Dictionary error"
            print "Bailing out..."
            sys.exit(99)

        self._base_broker_url = 'amqp_url'
        self._next_timed_ack_id = 0

        # Build ccd_list as if a config key is being used...
        for i in range (1, 21):
            self.CCD_LIST



        self.JOB_SCBD = JobScoreboard(job_db_instance)
        #self.TO_DO_SCBD = ToDoScoreboard(backlog_db_instance)
        self.ACK_SCBD = AckScoreboard(ack_db_instance)
        self.STATE_SCBD = StateScoreboard(state_db_instance, ddict)

        # Messages from both Base Foreman AND OCS Bridge
        self._OCS_msg_actions = { 'START': self.process_start_command,
                              'ENABLE': self.process_enable_command,
                              'DISABLE': self.process_disable_command,
                              'STANDBY': self.process_standby_command,
                              'EXIT': self.process_exit_command,
                              'FAULT': self.process_fault_command,
                              'OFFLINE': self.process_offline_command,
                              'NEXT_VISIT': self.process_next_visit_event,
                              'START_INTEGRATION': self.process_start_integration_event,
                              'READOUT': self.process_readout_event,
                              'TELEMETRY': self.process_telemetry }

        self._foreman_msg_actions = { 'FOREMAN_HEALTH_ACK': self.process_ack,
                              'NEW_SESSION_ACK': self.process_ack,
                              'AR_NEXT_VISIT_ACK': self.process_ack,
                              'AR_START_INTEGRATION_ACK': self.process_ack,
                              'AR_READOUT_ACK': self.process_ack,
                              'NEW_JOB_ACK': self.process_ack }


        self._base_broker_url = "amqp://" + self._base_name + ":" + self._base_passwd + "@" + str(self._base_broker_addr)
        LOGGER.info('Building _base_broker_url. Result is %s', self._base_broker_url)

        self.setup_publishers()
        self.setup_consumers()



    def setup_consumers(self):
        LOGGER.info('Setting up consumers on %s', self._base_broker_url)
        LOGGER.info('Running start_new_thread on all consumer methods')

        self._ocs_bdg_consumer = Consumer(self._base_broker_url, self.OCS_BDG_PUBLISH, "YAML")
        try:
            thread.start_new_thread( self.run_ocs_bdg_consumer, ("thread-dmcs-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start DMCS consumer thread, exiting...')
            print "Cannot start consumer!"
            #sys.exit(99)


        self._ack_consumer = Consumer(self._base_broker_url, self.AR_FOREMAN_ACK_PUBLISH, "YAML")
        try:
            thread.start_new_thread( self.run_ack_consumer, ("thread-ack-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start ACK consumer thread, exiting...')
            print "Cannot start consumer!"
            #sys.exit(102)

        LOGGER.info('Finished starting all three consumer threads')


    def run_ocs_bdg_consumer(self, threadname, delay):
        self._ocs_bdg_consumer.run(self.on_ocs_message)



    def run_ocs_consumer(self, threadname, delay):
        self._ocs_consumer.run(self.on_ocs_message)

    def run_ack_consumer(self, threadname, delay):
        self._ack_consumer.run(self.on_ack_message)



    def setup_publishers(self):
        LOGGER.info('Setting up Base publisher on %s', self._base_broker_url)
        self._publisher = SimplePublisher(self._base_broker_url, "YAML")



    def on_ocs_message(self, ch, method, properties, body):
        #msg_dict = yaml.load(body) 
        msg_dict = body 
        LOGGER.info('In DMCS message callback')
        LOGGER.debug('Thread in DMCS callback is %s', thread.get_ident())
        LOGGER.info('Message from DMCS callback message body is: %s', str(msg_dict))

        handler = self._OCS_msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    
    def on_foreman_message(self, ch, method, properties, body):
        #msg_dict = yaml.load(body) 
        msg_dict = body 
        LOGGER.info('In DMCS message callback')
        LOGGER.debug('Thread in DMCS callback is %s', thread.get_ident())
        LOGGER.info('Message from DMCS callback message body is: %s', str(msg_dict))

        handler = self._foreman_msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def on_ack_message(self, ch, method, properties, body):
        msg_dict = body 
        print "ACK MSG BODY is:\n%s" % body
        LOGGER.info('In ACK message callback')
        LOGGER.debug('Thread in ACK callback is %s', thread.get_ident())
        LOGGER.info('Message from ACK callback message body is: %s', str(msg_dict))

        handler = self._foreman_msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

   #==================================================================================== 
   # The following functions map to the state transition commands that the OCS will generate
   # It is noted here rather than in method documentation below (to keep descriptions simple),
   # that a FaultState is reachable from StandbyState, DisableState, and EnableState.

    def process_standby_command(self, msg):
        """StandbyState is the initial system stste after the system comes up and makes connection with DDS.
           WHENEVER the StandbyState is entered, a new Session_ID is created. 
           IOW, the DMCS wakes up to find itself in StandbyState.
           Communication with DDS is expected and needed in ths state.
           There are two transitions INTO StandbyState:
               1) Component/system wake up
               2) Standby - the transition command from DisableState to StandbyState. THIS TRANSITION IS THE
                  ONE THAT THIS METHOD ADDRESSES.

           There are two transitions OUT of StandbyState:
               1) Start - the command from SandbyState to DisableState will be
                  accompanied by configuration settings, such as interface version, DM cfg, etc.
               2) Exit - effectively ends session by moving state to OfflineState which 
                  has only one 'out'  state transition - to FinalState.
        """
        # Extract device arg
        device = msg['DEVICE']
        if device == "AR":
            self.STATE_SCBD.set_archive_state("STANDBY")
        if device == "PP":
            self.STATE_SCBD.set_prompt_process_state("STANDBY")
        if device == "CU":
            self.STATE_SCBD.set_catchup_archive_state("STANDBY")

        # send new session id to all
        session_id = self.STATE_SCBD.get_next_session_id()
        acks = self.send_new_session_msg(session_id)

        self.ack_timer(2)

        # Check ack response
        for a in acks:
            ack_responses = self.ACK_SCBD.get_components_for_timed_ack(a)

        ## XXX FIX  Do error trapping below
        if ack_responses == None:
            print "BIG Problem handling new session ack"


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
        # Extract device arg
        device = msg['DEVICE']
        if device == "AR":
            self.STATE_SCBD.set_archive_state("DISABLE")
        if device == "PP":
            self.STATE_SCBD.set_prompt_process_state("DISABLE")
        if device == "CU":
            self.STATE_SCBD.set_catchup_archive_state("DISABLE")


    def process_enable_command(self, msg):
        print "Processing Enable Command"
        """Transition from DisableState to EnableState. Full operation is capable after this transition.

        """
        # Extract device arg
        device = msg['DEVICE']
        if device == "AR":
            self.STATE_SCBD.set_archive_state("ENABLE")
        if device == "PP":
            self.STATE_SCBD.set_prompt_process_state("ENABLE")
        if device == "CU":
            self.STATE_SCBD.set_catchup_archive_state("ENABLE")



    def process_exit_command(self, msg):
        """Transition from StandbyState to OfflineState. Catch up work could conceivably 
           be done in OfflineState. There will be no contact with DDS, however. The only
           available transition is from OfflineState to Final...which is 'off.' 
           Any needed entities to be persisted beteen starts should happen after this transition. 
           The system cannot be brought back up to EnableState from OfflineState.

           When this method is called, DMCS should finish up any running jobs, and then 
           begin working on the TO-DO queue. If the TO-DO queue is empty, persist and shut down.

           Because the DDS is not reachable in the state resulting from this command, and 
           telemetry from tasks done on the TO-DO queue must be staged, and then sent when 
           the system returns to StandbyState.
        
        """
        # Extract device arg
        device = msg['DEVICE']
        if device == "AR":
            self.STATE_SCBD.set_archive_state("EXIT")
        if device == "PP":
            self.STATE_SCBD.set_prompt_process_state("EXIT")
        if device == "CU":
            self.STATE_SCBD.set_catchup_archive_state("EXIT")



    def process_next_visit_event(self, params):
        # Send next visit info to any devices in enable state
        # Keep track of current Next Visit for each device.

        # First, get dict of devices in Enable state with their consume queues
        visit_id = params['VISIT_ID']
        self.JOB_SCBD.set_visit_id(visit_id)
        enabled_devices = self.STATE_SCBD.get_devices_by_state(self.ENABLE)

        acks = []
        for k in enabled_devices.keys():
            consume_queue = enabled_devices[k]
            ack = self.get_next_timed_ack_id("NEXT_VISIT_ACK")
            acks.append(ack)
            msg = {}
            msg[MSG_TYPE] = "NEXT_VISIT"
            msg[ACK_ID] = ack
            msg['VISIT_ID'] = params['VISIT_ID']
            msg['BORE_SIGHT'] = params['BORE_SIGHT']
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
        # Msg should have session, latest visit_id, job_num, ccd lists and image_id

        image_id = params['IMAGE_ID']
        ## Setting to Archive for now...
        device = params['DEVICE']
        job_num = self.STATE_SCBD.get_next_job_num(device)
        self.JOB_SCBD.set_current_device_job(job_num, device)

        ## CCD List will eventually be derived from config key. For now, using a list set in this class
        ccd_list = self.CCD_LIST
        visit_id = self.JOB_SCBD.get_current_visit()
        self.JOB_SCBD.add_job(job_num, image_id, visit_id, ccd_list)

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

        self.ack_timer(3)
        ## XXX Don't check for responses right now...


####### # Right now, using only Archive...
#        enabled_devices = self.STATE_SCBD.get_enabled_devices()
#        ack_prefix = 
#        acks = {}
#        for k in enabled_devices.keys():
#            consume_queue = enabled_devices[k]
#            ack = self.get_next_timed_ack_id("NEXT_VISIT_ACK")
#            acks.append(ack)
#            self._publisher.publish_message(consume_queue, msg)




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

    def enter_fault_state(self):
        pass

    def process_start_command(self):
        pass

    def process_fault_command(self):
        pass

    def process_offline_command(self):
        pass


    def process_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)
       
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
            
 


    def get_next_timed_ack_id(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        retval = ack_type + "_" + str(self._next_timed_ack_id).zfill(6)
        return retval 


    def ack_timer(self, seconds):
        sleep(seconds)
        return True

    def purge_broker(self):
        #This will either move to an external script, or be done dynamically by reading cfg file
        os.system('rabbitmqctl -p /tester purge_queue f_consume')
        os.system('rabbitmqctl -p /tester purge_queue forwarder_publish')
        os.system('rabbitmqctl -p /tester purge_queue ack_publish')
        os.system('rabbitmqctl -p /tester purge_queue dmcs_consume')
        os.system('rabbitmqctl -p /tester purge_queue ncsa_consume')

        os.system('rabbitmqctl -p /bunny purge_queue forwarder_publish')
        os.system('rabbitmqctl -p /bunny purge_queue ack_publish')
        os.system('rabbitmqctl -p /bunny purge_queue F1_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F2_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F3_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F4_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F5_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F6_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F7_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F8_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F9_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F10_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F11_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F12_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F13_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F14_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F15_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F16_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F17_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F18_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F19_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F20_consume')
        os.system('rabbitmqctl -p /bunny purge_queue F21_consume')


def main():
    logging.basicConfig(filename='logs/BaseForeman.log', level=logging.INFO, format=LOG_FORMAT)
    dmsc = DMCS()
    print "Beginning DMCS event loop..."
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print ""
    print "DMCS Done."


if __name__ == "__main__": main()
