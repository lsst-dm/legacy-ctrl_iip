import toolsmod
from toolsmod import get_timestamp
import logging
import pika
import redis
import yaml
import sys, traceback
import os, os.path
import time
import datetime
from time import sleep
import _thread
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
logging.basicConfig(filename='logs/DMCS.log', level=logging.DEBUG, format=LOG_FORMAT)


class DMCS:
    """As this set of consumer callbacks cannot block for the lengthy time some tasks (such as readouts)
       will take, a thread must poll for acks and handle accordingly. Tasks will be issued, and
       then a cyclical thread will read through acks and update scoreboards accordingly.

       Another thing that must happen here, is that state should be tracked in a hash specific to each
       device, each 'last state' must be pushed on to the RHS of a list structure for that particular
       commandable device. 
    """

    ACK_SCBD = None
    STATE_SCBD = None
    BACKLOG_SCBD = None
    OCS_BDG_PUBLISH = "ocs_dmcs_consume"  #Messages from OCS Bridge
    DMCS_OCS_PUBLISH = "dmcs_ocs_publish"  #Messages to OCS Bridge
    AR_FOREMAN_ACK_PUBLISH = "dmcs_ack_consume" #Used for Foreman comm
    DEFAULT_CFG_FILE = 'L1SystemCfg.yaml'
    CCD_LIST = [] 


    def __init__(self, filename=None):
        toolsmod.singleton(self)
        LOGGER.info('DMCS Init beginning')

        self._config_file = 'L1SystemCfg.yaml'
        if filename != None:
            self._config_file = filename


        LOGGER.info('Reading YAML Config file %s' % self._config_file)

        try:
            cdm = toolsmod.intake_yaml_file(self._config_file)
        except IOError as e:
            trace = traceback.print_exc()
            emsg = "Unable to find CFG Yaml file %s\n" % self._config_file
            LOGGER.critical(emsg + trace)
            sys.exit(101) 

        LOGGER.info('Extracting values from Config dictionary')
        self.extract_config_values(cdm)

        # Run queue purges in rabbitmqctl
        #self.purge_broker(broker_vhost, queue_purges)

        self._next_timed_ack_id = self.init_ack_id()


        LOGGER.info('Setting up DMCS Scoreboards')
        self.BACKLOG_SCBD = BacklogScoreboard('DMCS_BACKLOG_SCBD', self.backlog_db_instance)
        self.ACK_SCBD = AckScoreboard('DMCS_ACK_SCBD', self.ack_db_instance)
        self.STATE_SCBD = StateScoreboard('DMCS_STATE_SCBD', self.state_db_instance, self.ddict)


        # Messages from OCS Bridge
        self._OCS_msg_actions = { 'ENTER_CONTROL': self.process_enter_control_command,
                              'START': self.process_start_command,
                              'STANDBY': self.process_standby_command,
                              'DISABLE': self.process_disable_command,
                              'ENABLE': self.process_enable_command,
                              'SET_VALUE': self.process_set_value_command,
                              'FAULT': self.process_fault_command,
                              'EXIT_CONTROL': self.process_exit_control_command,
                              'ABORT': self.process_abort_command,
                              'STOP': self.process_stop_command,
                              'NEXT_VISIT': self.process_next_visit_event,
                              'START_INTEGRATION': self.process_start_integration_event,
                              'READOUT': self.process_readout_event,
                              'TELEMETRY': self.process_telemetry }

        self._foreman_msg_actions = { 'FOREMAN_HEALTH_ACK': self.process_ack,
                              'PP_NEW_SESSION_ACK': self.process_ack,
                              'AR_NEW_SESSION_ACK': self.process_ack,
                              'CU_NEW_SESSION_ACK': self.process_ack,
                              'SP_NEW_SESSION_ACK': self.process_ack,
                              'AR_NEXT_VISIT_ACK': self.process_ack,
                              'PP_NEXT_VISIT_ACK': self.process_ack,
                              'AR_START_INTEGRATION_ACK': self.process_ack,
                              'PP_START_INTEGRATION_ACK': self.process_ack,
                              'AR_READOUT_ACK': self.process_readout_results_ack,
                              'PP_READOUT_ACK': self.process_readout_results_ack,
                              'PENDING_ACK': self.process_pending_ack,
                              'NEW_JOB_ACK': self.process_ack }


        self._base_broker_url = "amqp://" + self._msg_name + ":" + \
                                            self._msg_passwd + "@" + \
                                            str(self._base_broker_addr)
        LOGGER.info('Building _base_broker_url. Result is %s', self._base_broker_url)


        self.pub_base_broker_url = "amqp://" + self._pub_name + ":" + \
                                            self._pub_passwd + "@" + \
                                            str(self._base_broker_addr)
        LOGGER.info('Building publishing _base_broker_url. Result is %s', self.pub_base_broker_url)

        LOGGER.info('DMCS consumer setup')
        self.setup_consumers()

        LOGGER.info('DMCS publisher setup')
        self.setup_publishers()


        # Check health of all devices

        # All devices wake up in OFFLINE state
        self.STATE_SCBD.set_device_state("AR","OFFLINE")

        self.STATE_SCBD.set_device_state("PP","OFFLINE")

        self.STATE_SCBD.set_device_state("CU","OFFLINE")

        self.STATE_SCBD.add_device_cfg_keys('AR', self.ar_cfg_keys)
        print("CFG_KEYS is %s" % self.ar_cfg_keys)
        self.STATE_SCBD.set_device_cfg_key('AR',self.STATE_SCBD.get_cfg_from_cfgs('AR', 0))
        #self.STATE_SCBD.set_device_cfg_key('AR','archiver-Normal')
        print("Chosen CFG Key is: %s" % self.STATE_SCBD.get_cfg_from_cfgs('AR', 0))

        self.STATE_SCBD.add_device_cfg_keys('PP', self.pp_cfg_keys)
        self.STATE_SCBD.set_device_cfg_key('PP',self.STATE_SCBD.get_cfg_from_cfgs('PP', 0))

        self.STATE_SCBD.add_device_cfg_keys('CU', self.cu_cfg_keys)
        self.STATE_SCBD.set_device_cfg_key('CU',self.STATE_SCBD.get_cfg_from_cfgs('CU', 0))

        self.send_appropriate_events_by_state('AR', 'OFFLINE')
        self.send_appropriate_events_by_state('PP', 'OFFLINE')
        self.send_appropriate_events_by_state('CU', 'OFFLINE')
        LOGGER.info('DMCS Init complete')


    def init_ack_id(self):
        if os.path.isfile(self.dmcs_ack_id_file):
            val = toolsmod.intake_yaml_file(self.dmcs_ack_id_file)
            current_id = val['CURRENT_ACK_ID'] + 1
            if current_id > 999900:
                current_id = 1
            val['CURRENT_ACK_ID'] = current_id
            toolsmod.export_yaml_file(self.dmcs_ack_id_file, val)
            return current_id
        else:
            current_id = 1
            val = {}
            val['CURRENT_ACK_ID'] = current_id
            toolsmod.export_yaml_file(self.dmcs_ack_id_file, val)
            return current_id


    def setup_consumers(self):
        LOGGER.info('Setting up consumers on %s', self._base_broker_url)
        LOGGER.info('Running start_new_thread on all DMCS consumer methods')

        self._ocs_bdg_consumer = Consumer(self._base_broker_url, self.OCS_BDG_PUBLISH, "YAML")
        try:
            _thread.start_new_thread( self.run_ocs_bdg_consumer, ("thread-dmcs-consumer", 2,) )
        except Exception as e: # Catching naked exception as thread exceptions can be many
            trace = traceback.print_exc()
            emsg = "Unable to start new thread for OCS Bridge consumer"
            LOGGER.critical(emsg + trace)
            LOGGER.critical('Cannot start OCS Bridge consumer thread for DMCS, exiting...')
            sys.exit(103)


        self._ack_consumer = Consumer(self._base_broker_url, self.AR_FOREMAN_ACK_PUBLISH, "YAML")
        try:
            _thread.start_new_thread( self.run_ack_consumer, ("thread-ack-consumer", 2,) )
        except Exception as e:
            trace = traceback.print_exc()
            emsg = "Unable to start new thread for OCS Bridge consumer"
            LOGGER.critical(emsg + trace)
            LOGGER.critical('Cannot start ACK consumer thread for DMCS, exiting...')
            print("Cannot start ACK consumer for DMCS!")
            sys.exit(104)

        LOGGER.info('Finished starting all three consumer threads')


    def run_ocs_bdg_consumer(self, threadname, delay):
        LOGGER.debug('Thread ID in OCS Bridge consumer callback is %s', _thread.get_ident())
        self._ocs_bdg_consumer.run(self.on_ocs_message)

    def run_ack_consumer(self, threadname, delay):
        LOGGER.debug('Thread ID in ACK consumer callback is %s', _thread.get_ident())
        self._ack_consumer.run(self.on_ack_message)


    def setup_publishers(self):
        LOGGER.info('Setting up Base publisher on %s', self.pub_base_broker_url)
        self._publisher = SimplePublisher(self.pub_base_broker_url, YAML)


    def on_ocs_message(self, ch, method, properties, msg_dict):
        print("DUMPING msg_dict: %s" % msg_dict)
        LOGGER.info('Processing message in OCS message callback')
        LOGGER.debug('Thread in OCS message callback of DMCS is %s', _thread.get_ident())
        LOGGER.debug('Message and properties from DMCS callback message body is: %s', (str(msg_dict),properties))

        handler = self._OCS_msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def on_ack_message(self, ch, method, properties, msg_dict):
        LOGGER.info('Processing message in ACK message callback')
        LOGGER.debug('Thread in ACK callback od DMCS is %s', _thread.get_ident())
        LOGGER.debug('Message and properties from ACK callback message body is: %s', (str(msg_dict),properties))

        handler = self._foreman_msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


    def process_enter_control_command(self, msg):
        new_state = toolsmod.next_state[msg['MSG_TYPE']]
        transition_check = self.validate_transition(new_state, msg)


    def process_start_command(self, msg):
        new_state = toolsmod.next_state[msg['MSG_TYPE']]
        transition_check = self.validate_transition(new_state, msg)


    def process_standby_command(self, msg):
        new_state = toolsmod.next_state[msg['MSG_TYPE']]
        transition_check = self.validate_transition(new_state, msg)

        if transition_check:
            # send new session id to all
            session_id = self.STATE_SCBD.get_next_session_id()
            self.send_new_session_msg(session_id)


    def process_disable_command(self, msg):
        new_state = toolsmod.next_state[msg['MSG_TYPE']]
        transition_check = self.validate_transition(new_state, msg)


    def process_enable_command(self, msg):
        new_state = toolsmod.next_state[msg['MSG_TYPE']]
        transition_check = self.validate_transition(new_state, msg)


    def process_set_value_command(self, msg):
        device = msg['DEVICE']
        ack_msg = {}
        ack_msg['MSG_TYPE'] = msg['MSG_TYPE'] + "_ACK"
        ack_msg['ACK_ID'] = msg['ACK_ID']

        current_state = self.STATE_SCBD.get_device_state(device)
        if current_state == 'ENABLE':
            value = msg['VALUE']
            # Try and do something with value...
            result = self.set_value(value)
            if result:
                ack_msg['ACK_BOOL'] = True 
                ack_msg['ACK_STATEMENT'] = "Device " + device + " set to new value: " + str(value)
            else:
                ack_msg['ACK_BOOL'] = False 
                ack_msg['ACK_STATEMENT'] = "Value " + str(value) + " is not valid for " + device
        else:
            ack_msg['ACK_BOOL'] = False 
            ack_msg['ACK_STATEMENT'] = "Current state is " + current_state + ". Device \
                                       state must be in ENABLE state for SET_VALUE command."

        self._publisher.publish_message(self.DMCS_OCS_PUBLISH, ack_msg)



    def process_fault_command(self, msg):
        pass


    def process_exit_control_command(self, msg):
        new_state = toolsmod.next_state[msg['MSG_TYPE']]
        transition_check = self.validate_transition(new_state, msg)


    def process_abort_command(self, msg):
        new_state = toolsmod.next_state[msg['MSG_TYPE']]
        # Send out ABORT messages!!!
        transition_check = self.validate_transition(new_state, msg)


    def process_stop_command(self, msg):
        new_state = toolsmod.next_state[msg['MSG_TYPE']]
        transition_check = self.validate_transition(new_state, msg)


    def process_next_visit_event(self, params):
        # Send next visit info to any devices in enable state
        # Keep track of current Next Visit for each device.

        # First, get dict of devices in Enable state with their consume queues
        visit_id = params['VISIT_ID']
        self.STATE_SCBD.set_visit_id(visit_id)
        enabled_devices = self.STATE_SCBD.get_devices_by_state(ENABLE)
        LOGGER.debug("Enabled device list is:")
        LOGGER.debug(enabled_devices)
        session_id = self.STATE_SCBD.get_current_session()

        acks = []
        for k in list(enabled_devices.keys()):
            consume_queue = enabled_devices[k]
            ## FIXME - Must each enabled device use its own ack_id? Or
            ## can we use the same method for broadcasting Forwarder messages?  
            ack = self.get_next_timed_ack_id(k + "_NEXT_VISIT_ACK")
            acks.append(ack)
            msg = {}
            msg[MSG_TYPE] = k + '_NEXT_VISIT'
            msg[ACK_ID] = ack
            msg['SESSION_ID'] = session_id
            msg[VISIT_ID] = params[VISIT_ID]
            msg[BORE_SIGHT] = params['BORE_SIGHT']
            msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
            LOGGER.debug("Sending next visit msg %s to %s at queue %s" % (msg, k, consume_queue))
            self._publisher.publish_message(consume_queue, msg)

        self.ack_timer(2)
        for a in acks:
            ack_responses = self.ACK_SCBD.get_components_for_timed_ack(a)

            if ack_responses != None:
                print("Printing ack responses...")
                print(ack_responses)
                responses = list(ack_responses.keys())
                print("Printing ack responses...")
                print(responses)
                for response in responses:
                    if ack_responses[response]['ACK_BOOL'] == False:
                        # Mark this device as messed up...maybe enter fault.
                        pass 
            else:
                #Enter a fault state, as no devices are responding
                pass
            
            


    def process_start_integration_event(self, params):
        # Send start int message to all enabled devices, with details of job...include new job_num

        ## FIX - see temp hack below...
        ## CCD List will eventually be derived from config key. For now, using a list set in top of this class
        ccd_list = self.CCD_LIST
        msg_params = {}
        # visit_id and image_id msg_params *could* be set in one line, BUT: the values are needed again below...
        visit_id = self.STATE_SCBD.get_current_visit()
        msg_params[VISIT_ID] = visit_id
        image_id = params[IMAGE_ID]  # NOTE: Assumes same image_id for all devices readout
        msg_params[IMAGE_ID] = image_id
        msg_params['RESPONSE_QUEUE'] = 'dmcs_ack_consume'
        msg_params['CCD_LIST'] = ccd_list
        session_id = self.STATE_SCBD.get_current_session()
        msg_params['SESSION_ID'] = session_id


        enabled_devices = self.STATE_SCBD.get_devices_by_state('ENABLE')
        acks = []
        for k in list(enabled_devices.keys()):
            ack_id = self.get_next_timed_ack_id( str(k) + "_START_INT_ACK")
            acks.append(ack_id)
            job_num = self.STATE_SCBD.get_next_job_num( session_id)
            print("--- JOB NUM is %s ---" % job_num)
            self.STATE_SCBD.add_job(job_num, image_id, visit_id, ccd_list)
            self.STATE_SCBD.set_value_for_job(job_num, 'DEVICE', str(k))
            self.STATE_SCBD.set_current_device_job(job_num, str(k))
            self.STATE_SCBD.set_job_state(job_num, "DISPATCHED")
            msg_params[MSG_TYPE] = k + '_START_INTEGRATION'
            msg_params[JOB_NUM] = job_num
            msg_params[ACK_ID] = ack_id
            self._publisher.publish_message(self.STATE_SCBD.get_device_consume_queue(k), msg_params)


        wait_time = 5  # seconds...
        self.set_pending_nonblock_acks(acks, wait_time)

 
    def process_readout_event(self, params):
        ## FIX - see temp hack below...
        ## CCD List will eventually be derived from config key. For now, using a list set in top of this class
        ccd_list = self.CCD_LIST

        msg_params = {}
        msg_params[VISIT_ID] = self.STATE_SCBD.get_current_visit()
        msg_params[IMAGE_ID] = params[IMAGE_ID]  # NOTE: Assumes same image_id for all devices readout
        msg_params['RESPONSE_QUEUE'] = 'dmcs_ack_consume'
        session_id = self.STATE_SCBD.get_current_session()
        msg_params['SESSION_ID'] = session_id

        enabled_devices = self.STATE_SCBD.get_devices_by_state('ENABLE')
        acks = []
        for k in list(enabled_devices.keys()):
            ack_id = self.get_next_timed_ack_id( str(k) + "_READOUT_ACK")
            acks.append(ack_id)
            job_num = self.STATE_SCBD.get_current_device_job(str(k))
            msg_params[MSG_TYPE] = k + '_READOUT'
            msg_params[ACK_ID] = ack_id
            msg_params[JOB_NUM] = job_num
            self.STATE_SCBD.set_job_state(job_num, "READOUT")
            self._publisher.publish_message(self.STATE_SCBD.get_device_consume_queue(k), msg_params)


        wait_time = 5  # seconds...
        self.set_pending_nonblock_acks(acks, wait_time)
        # add in two additional acks for format and transfer complete


    def process_telemetry(self, msg):
        pass


    def process_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)


    def process_pending_ack(self, params):
        self.ACK_SCBD.add_pending_nonblock_ack(params)


    def process_readout_results_ack(params):
        # FIXME make certain devices/job_nums are kept separate so OCS can be informed of results properly.
        job_num = params[JOB_NUM]
        results = params['RESULTS_LIST']

        # Mark job number done
        self.STATE_SCBD.set_job_state(job_num, "COMPLETE")

        # Store results for job with that job
        self.STATE_SCBD.set_results_for_job(job_num, results)

        failed_list = []
        keez = list(results.keys())
        for kee in keez:
            ## No File == 0; Bad checksum == -1
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

        ack_ids = [] 
        msg = {}
        #msg['MSG_TYPE'] = 'NEW_SESSION'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['SESSION_ID'] = session_id

        ddict = self.STATE_SCBD.get_devices()
        for k in list(ddict.keys()):
            msg['MSG_TYPE'] = k + '_NEW_SESSION'
            consume_queue = ddict[k]
            ack_id = self.get_next_timed_ack_id(k + "_NEW_SESSION_ACK")
            msg['ACK_ID'] = ack_id
            ack_ids.append(ack_id)
            self._publisher.publish_message(consume_queue, msg)

        # Non-blocking Acks placed directly into ack_scoreboard
        wait_time = 3  # seconds...
        self.set_pending_nonblock_acks(ack_ids, wait_time)


    def validate_transition(self, new_state, msg_in):
        device = msg_in['DEVICE']
        cfg_response = ""
        current_state = self.STATE_SCBD.get_device_state(device)
            
        current_index = toolsmod.state_enumeration[current_state]
        new_index = toolsmod.state_enumeration[new_state]

        if msg_in['MSG_TYPE'] == 'START': 
            if 'CFG_KEY' in msg_in:
                good_cfg = self.STATE_SCBD.check_cfgs_for_cfg(device,msg_in['CFG_KEY'])
                if good_cfg:
                    cfg_result = self.STATE_SCBD.set_device_cfg_key(device, msg_in['CFG_KEY'])
                    cfg_response = " CFG Key set to %s" % msg_in['CFG_KEY']
                else:
                    cfg_response = " Bad CFG Key - remaining in %s" % current_state
                    self.send_ocs_ack(False, cfg_response, msg_in)
                    return False
        

        transition_is_valid = toolsmod.state_matrix[current_index][new_index]
        if transition_is_valid == True:
            self.STATE_SCBD.set_device_state(device, new_state)
            response = str(device) + " device in " + new_state
            response = response + cfg_response
            self.send_ocs_ack(transition_is_valid, response, msg_in)
        else:
            response = "Invalid transition: " + str(current_state) + " to " + new_state
            #response = response + ". Device remaining in " + current_state + " state."
            self.send_ocs_ack(transition_is_valid, response, msg_in)

        return transition_is_valid
 

    def set_pending_nonblock_acks(self, acks, wait_time):
        start_time = datetime.datetime.now().time()
        expiry_time = self.add_seconds(start_time, wait_time)
        ack_msg = {}
        ack_msg[MSG_TYPE] = 'PENDING_ACK'
        ack_msg['EXPIRY_TIME'] = expiry_time
        for ack in acks:
            ack_msg[ACK_ID] = ack
            self._publisher.publish_message("dmcs_ack_consume", ack_msg)


    def send_ocs_ack(self, transition_check, response, msg_in):
        message = {}
        message['MSG_TYPE'] = msg_in['MSG_TYPE'] + "_ACK"
        message['DEVICE'] = msg_in['DEVICE']
        message['ACK_ID'] = msg_in['ACK_ID']
        message['ACK_BOOL'] = transition_check
        message['ACK_STATEMENT'] = response
        self._publisher.publish_message(self.DMCS_OCS_PUBLISH, message) 

        if transition_check:
            self.send_appropriate_events_by_state(msg_in['DEVICE'], msg_in['MSG_TYPE'])


    def send_appropriate_events_by_state(self, dev, transition):

        if transition == 'START':
            self.send_setting_applied_event(dev)
            self.send_summary_state_event(dev)
            self.send_applied_setting_match_start_event(dev)
        elif transition == 'ENABLE':
            self.send_summary_state_event(dev)
        elif transition == 'DISABLE':
            self.send_summary_state_event(dev)
        elif transition == 'STANDBY':
            self.send_summary_state_event(dev)
        elif transition == 'EXIT_CONTROL':
            self.send_summary_state_event(dev)
        elif transition == 'FAULT':
            self.send_error_code_event(dev)
        elif transition == 'OFFLINE':
            self.send_summary_state_event(dev)
        elif transition == 'ENTER_CONTROL':
            self.send_summary_state_event(dev)
            self.send_recommended_setting_versions_event(dev)


    def send_summary_state_event(self, device):
        message = {}
        message[MSG_TYPE] = 'SUMMARY_STATE_EVENT'
        message['DEVICE'] = device
        message['CURRENT_STATE'] = toolsmod.summary_state_enum[self.STATE_SCBD.get_device_state(device)]
        self._publisher.publish_message(self.DMCS_OCS_PUBLISH, message)


    def send_recommended_setting_versions_event(self, device):
        message = {}
        message[MSG_TYPE] = 'RECOMMENDED_SETTINGS_VERSION_EVENT'
        message['DEVICE'] = device
        message['CFG_KEY'] = self.STATE_SCBD.get_device_cfg_key(device)
        print(" REAL_CFG_KEY is %s" % self.STATE_SCBD.get_device_cfg_key(device))
        print("Now CFG_KEY being sent is : %s" % message['CFG_KEY'])
        self._publisher.publish_message(self.DMCS_OCS_PUBLISH, message)


    def send_setting_applied_event(self, device):
        message = {}
        message[MSG_TYPE] = 'SETTINGS_APPLIED_EVENT'
        message['DEVICE'] = device
        message['APPLIED'] = True
        self._publisher.publish_message(self.DMCS_OCS_PUBLISH, message)


    def send_applied_setting_match_start_event(self, device):
        message = {}
        message[MSG_TYPE] = 'APPLIED_SETTINGS_MATCH_START_EVENT'
        message['DEVICE'] = device
        message['APPLIED'] = True
        self._publisher.publish_message(self.DMCS_OCS_PUBLISH, message)


    def send_error_code_event(self, device):
        message = {}
        message[MSG_TYPE] = 'ERROR_CODE_EVENT'
        message['DEVICE'] = device
        message['ERROR_CODE'] = 102
        self._publisher.publish_message(self.DMCS_OCS_PUBLISH, message)


    def get_next_timed_ack_id(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        val = {}
        val['CURRENT_ACK_ID'] = self._next_timed_ack_id
        toolsmod.export_yaml_file(self.dmcs_ack_id_file, val)
        retval = ack_type + "_" + str(self._next_timed_ack_id).zfill(6)
        return retval 


    def ack_timer(self, seconds):
        sleep(seconds)
        return True

    def extract_config_values(self, cdm):
        try:
            self._msg_name = cdm[ROOT]['DMCS_BROKER_NAME']      # Message broker user & passwd
            self._msg_passwd = cdm[ROOT]['DMCS_BROKER_PASSWD']
            self._pub_name = cdm[ROOT]['DMCS_BROKER_PUB_NAME']
            self._pub_passwd = cdm[ROOT]['DMCS_BROKER_PUB_PASSWD']
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self.ddict = cdm[ROOT]['FOREMAN_CONSUME_QUEUES']
            self.state_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_STATE_SCBD']
            self.ack_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_ACK_SCBD']
            self.backlog_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_BACKLOG_SCBD']
            self.CCD_LIST = cdm[ROOT]['CCD_LIST']
            self.ar_cfg_keys = cdm[ROOT]['AR_CFG_KEYS']
            self.pp_cfg_keys = cdm[ROOT]['PP_CFG_KEYS']
            self.cu_cfg_keys = cdm[ROOT]['CU_CFG_KEYS']
            broker_vhost = cdm[ROOT]['BROKER_VHOST']
            queue_purges = cdm[ROOT]['QUEUE_PURGES']
            self.dmcs_ack_id_file = cdm[ROOT]['DMCS_ACK_ID_FILE']
        except KeyError as e:
            trace = traceback.print_exc()
            emsg = "Unable to find key in CDM representation of %s\n" % filename
            LOGGER.critical(emsg + trace)
            sys.exit(102)

        return True


    def add_seconds(self, intime, secs):
        basetime = datetime.datetime(100, 1, 1, intime.hour, intime.minute, intime.second)
        newtime = basetime + datetime.timedelta(seconds=secs)
        return newtime.time()


    def purge_broker(self, vhost, queues):
        for q in queues:
            cmd = "sudo rabbitmqctl -p " + vhost + " purge_queue " + q
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
    logging.basicConfig(filename='logs/DMCS.log', level=logging.INFO, format=LOG_FORMAT)
    dmsc = DMCS()
    print("Beginning DMCS event loop...")
    try:
        while 1:
            # dmcs.get_next_backlog_item() ???
            pass
    except KeyboardInterrupt:
        pass

    print("")
    print("DMCS Done.")


if __name__ == "__main__": main()
