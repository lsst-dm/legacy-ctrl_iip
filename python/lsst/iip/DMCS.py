import toolsmod
from toolsmod import get_timestamp
import logging
from logging.handlers import RotatingFileHandler
import pika
import redis
import yaml
import sys, traceback
import os, os.path
from subprocess import call
import time
import datetime
from pprint import pprint, pformat
from time import sleep
from threading import ThreadError
import threading
from ThreadManager import ThreadManager
from const import *
from Scoreboard import Scoreboard
from JobScoreboard import JobScoreboard
from AckScoreboard import AckScoreboard
from StateScoreboard import StateScoreboard
from BacklogScoreboard import BacklogScoreboard
from IncrScoreboard import IncrScoreboard
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from toolsmod import L1Error
from toolsmod import L1RedisError
from toolsmod import L1RabbitConnectionError

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
handler = RotatingFileHandler('logs/DMCS.log', maxBytes=2000000, backupCount = 10)
handler.setFormatter(LOG_FORMAT)
LOGGER.addHandler(handler)


class DMCS:
    """ The DMCS is the principle coordinator component for Level One System code.

        It sends and receives messages and events.

        Two message consumers (Consumer.py) are started within a ThreadManager object.
        The ThreadManager makes certain that the consumer threads are alive. If a 
        thread has died (due to an uncaught exception) the consumer is replaced by
        starting a new consumer in a new thread.

        The DMCS also maintains the state of the commandable devices. When an image is
        to be pulled from the DAQ and sent somewhere,, the DMCS issues a new Job 
        number to track the work.

        After init, most of this file is centered on methods that determine
        what to do when a certain message type is received.

        Finally, the DMCS keeps track of any failed jobs in a Backlog scoreboard.
    """

    DEFAULT_CFG_FILE = 'L1SystemCfg.yaml'
    OCS_BDG_PUBLISH = "ocs_dmcs_consume"  #Messages from OCS Bridge
    DMCS_OCS_PUBLISH = "dmcs_ocs_publish"  #Messages to OCS Bridge
    AR_FOREMAN_ACK_PUBLISH = "dmcs_ack_consume" #Used for Foreman comm
    EXPECTED_NUM_IMAGES = 'EXPECTED_NUM_IMAGES'
    OCS_CONSUMER_THREAD = "ocs_consumer_thread"
    ACK_CONSUMER_THREAD = "ack_consumer_thread"
    ERROR_CODE_PREFIX = 5500
    prp = toolsmod.prp
    DP = toolsmod.DP


    def __init__(self, filename=None):
        """ Create a new instance of the DMCS class. Initiate DMCS with config_file
            and store handler methods for each message type. Set up publishers and
            scoreboards. The multiple consumer threads run within a ThreadManager
            object that monitors their health, replaces them if they die, and 
            manages thread semaphores that allow the app to be shut down cleanly.

            :params filename: Default 'L1SystemCfg.yaml'. Can be overridden and
                    assigned by user; during unit testing, for example.

            :return: None.
        """
        toolsmod.singleton(self)
        LOGGER.info('DMCS Init beginning')

        self._config_file = self.DEFAULT_CFG_FILE
        if filename != None:
            self._config_file = filename

        LOGGER.info('Extracting values from Config dictionary')
        self.extract_config_values()

        # Run queue purges in rabbitmqctl
        #self.purge_broker(broker_vhost, queue_purges)

        # These two dicts call the correct handler method for the message_type of incoming messages
        self._OCS_msg_actions = { 'ENTER_CONTROL': self.process_enter_control_command,
                              'START': self.process_start_command,
                              'STANDBY': self.process_standby_command,
                              'DISABLE': self.process_disable_command,
                              'ENABLE': self.process_enable_command,
                              'SET_VALUE': self.process_set_value_command,
                              'EXIT_CONTROL': self.process_exit_control_command,
                              'ABORT': self.process_abort_command,
                              'STOP': self.process_stop_command,
                              'NEXT_VISIT': self.process_next_visit_event,
                              'START_INTEGRATION': self.process_start_integration_event,
                              'DMCS_AT_START_INTEGRATION': self.process_at_start_integration_event,
			      ###########################################################
                              'DMCS_HEADER_READY': self.process_header_ready_event,
                              'DMCS_AT_HEADER_READY': self.process_at_header_ready_event,
                              'DMCS_TCS_TARGET': self.process_target_visit_event, 
                              'DMCS_TAKE_IMAGES': self.process_ccs_take_images_event,
			      'DMCS_END_READOUT': self.process_end_readout, 
			      'DMCS_AT_END_READOUT': self.process_at_end_readout} 


        self._foreman_msg_actions = { 'FOREMAN_HEALTH_ACK': self.process_ack,
                              'PP_NEW_SESSION_ACK': self.process_ack,
                              'AR_NEW_SESSION_ACK': self.process_ack,
                              'CU_NEW_SESSION_ACK': self.process_ack,
                              'SP_NEW_SESSION_ACK': self.process_ack,
                              'AR_NEXT_VISIT_ACK': self.process_ack,
                              'PP_NEXT_VISIT_ACK': self.process_ack,
                              'AR_START_INTEGRATION_ACK': self.process_ack,
                              'AT_START_INTEGRATION_ACK': self.process_ack,
                              'PP_START_INTEGRATION_ACK': self.process_ack,
                              'AR_READOUT_ACK': self.process_readout_results_ack,
                              'PP_READOUT_ACK': self.process_readout_results_ack,
                              'PENDING_ACK': self.process_pending_ack,
                              'NEW_JOB_ACK': self.process_ack }

        self._fault_actions = { 'FAULT': self.process_fault }



        LOGGER.info('DMCS publisher setup')
        self.setup_publishers()

        self.setup_scoreboards()

        LOGGER.info('DMCS consumer setup')
        self.thread_manager = None
        self.setup_consumer_threads()

        self.init_ack_id()

        LOGGER.info('DMCS init complete')



    def init_ack_id(self):
        """ Create an ack_id for the message. If dmcs_ack_id_file is a valid path,
            increment it's current_ack_id. Start from 1 if exceeds 999900 or
            dmcs_ack_id_file does not exist, and store current_ack_id to
            dmcs_ack_id_file.

            :params: None.

            :return: None.
        """
        try: 
            ### FIX change to use redis db incr...
            self._next_timed_ack_id = 0
            if os.path.isfile(self.dmcs_ack_id_file):
                val = toolsmod.intake_yaml_file(self.dmcs_ack_id_file)
                current_id = val['CURRENT_ACK_ID'] + 1
                if current_id > 999900:
                    current_id = 1
                val['CURRENT_ACK_ID'] = current_id
                toolsmod.export_yaml_file(self.dmcs_ack_id_file, val)
                self._next_timed_ack_id = current_id
            else:
                current_id = 1
                val = {}
                val['CURRENT_ACK_ID'] = current_id
                toolsmod.export_yaml_file(self.dmcs_ack_id_file, val)
                self._next_timed_ack_id =  current_id
        except Exception as e: 
            LOGGER.error("DMCS unable to get init_ack_id: %s" % e.args) 
            print("DMCS unable to get init_ack_id: %s" % e.args) 
            raise L1Error("DMCS unable to get init_ack_id: %s" % e.args) 

    def setup_publishers(self):
        """ Set up base publisher with pub_base_broker_url by calling a new instance
            of SimplePublisher class.

            :params: None.

            :return: None.
        """
        self.pub_base_broker_url = "amqp://" + self._pub_name + ":" + \
                                            self._pub_passwd + "@" + \
                                            str(self._base_broker_addr)

        self.pub_fault_base_broker_url = "amqp://" + self._pub_fault_name + ":" + \
                                            self._pub_fault_passwd + "@" + \
                                            str(self._base_broker_addr)

        LOGGER.info('Building publishing pub_base_broker_url. Result is %s', self.pub_base_broker_url)        

        LOGGER.info('Setting up Base publisher ')
        try: 
            self._publisher = SimplePublisher(self.pub_base_broker_url, YAML)
            self._fault_publisher = SimplePublisher(self.pub_fault_base_broker_url, YAML)
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to setup_publishers: %s" % e.args) 
            print("DMCS unable to setup_publishers: %s" % e.args) 
            sys.exit(self.ERROR_CODE_PREFIX + 11)
        except Exception as e: 
            LOGGER.error("DMCS unable to setup_publishers: %s" % e.args) 
            print("DMCS unable to setup_publishers: %s" % e.args) 
            sys.exit(self.ERROR_CODE_PREFIX + 11)
        



    def on_ocs_message(self, ch, method, properties, msg_dict):
        """ Calls the appropriate OCS action handler according to message type.

            :params ch: Channel to message broker, unused unless testing.
            :params method: Delivery method from Pika, unused unless testing.
            :params properties: Properties from DMCS callback message body.
            :params msg_dict: A dictionary that stores the message body.

            :return: None.
        """
        print("In On OCS Msg, msg is: %s" % msg_dict)
        try: 
            ch.basic_ack(method.delivery_tag)
            LOGGER.info('Processing message in OCS message callback')
            LOGGER.debug('Message and properties from DMCS callback message body is: %s', 
                        (str(msg_dict),properties))

            print('Processing message in OCS message callback')
            print('Message and properties from DMCS callback message body is: %s', 
                        (str(msg_dict),properties))

            handler = self._OCS_msg_actions.get(msg_dict[MSG_TYPE])
            if handler == None:
                raise KeyError("In on_ocs_message; Received unknown MSG_TYPE: %s" % msg_dict[MSG_TYPE])
            result = handler(msg_dict)
        except KeyError as e:
            LOGGER.error("DMCS received unrecognized message type: %s" % e.args)
            if self.DP: 
                print("DMCS received unrecognized message type: %s" % e.args)
            raise L1Error("DMCS ecountering Error Code %s. %s" % (str(self.ERROR_CODE_PREFIX + 35), e.args))
        except Exception as e: 
            LOGGER.error("DMCS unable to on_ocs_message: %s" % e.args) 
            print("DMCS unable to on_ocs_message: %s" % e.args) 
            raise L1Error("DMCS unable to on_ocs_message: %s" % e.args) 
    


    def on_ack_message(self, ch, method, properties, msg_dict):
        """ Calls the appropriate foreman action handler according to message type.

            :params ch: Channel to message broker, unused unless testing.
            :params method: Delivery method from Pika, unused unless testing.
            :params properties: Properties from DMCS callback message body.
            :params msg_dict: A dictionary that stores the message body.

            :return: None.
        """
        try: 
            ch.basic_ack(method.delivery_tag) 
            LOGGER.info('Processing message in ACK message callback')
            LOGGER.debug('Message and properties from ACK callback message body is: %s', 
                         (str(msg_dict),properties))

            print('Processing message in ACK message callback')
            print('Message and properties from ACK callback message body is: %s', 
                         (str(msg_dict),properties))

            handler = self._foreman_msg_actions.get(msg_dict[MSG_TYPE])
            if handler == None:
                raise KeyError("In on_ack_message; Received unknown MSG_TYPE: %s" % msg_dict[MSG_TYPE])
            result = handler(msg_dict)
        except KeyError as e:
            LOGGER.error("DMCS received unrecognized message type: %s" % e.args)
            if self.DP: 
                print("DMCS received unrecognized message type: %s" % e.args)
            raise L1Error("DMCS ecountering Error Code %s. %s" % (str(self.ERROR_CODE_PREFIX + 35), e.args))
        except Exception as e: 
            LOGGER.error("DMCS unable to on_ack_message: %s" % e.args) 
            print("DMCS unable to on_ack_message: %s" % e.args) 
            raise L1Error("DMCS unable to on_ack_message: %s" % e.args) 


    def on_fault_message(self, ch, method, properties, msg_dict):
        try:
            ch.basic_ack(method.delivery_tag) 
            LOGGER.info('Processing message in FAULT message callback')
            LOGGER.debug('Message and properties from FAULT callback message body are: %s and %s' % 
                         (pformat(str(msg_dict)), pformat(properties)))
    
            err_code = msg_dict['ERR_CODE']
            desc = msg_dict['DESCRIPTION']
            LOGGER.critical("DMCS received fault message with error code %s -- %s" % (err_code,desc))
            if self.DP: 
                print("DMCS received fault message, error code type: %s and description %s" % (err_code,desc))
        finally:
            self.process_fault(msg_dict)



    ### Remaining methods in this class are workhorse methods for the running threads

    def process_enter_control_command(self, msg):
        """ Pass the next state of the message transition (retrived from toolsmod.py)
            into validate_transition.

            :params msg: The message to be processed.

            :return: None.
        """
        try: 
            new_state = toolsmod.next_state[msg['MSG_TYPE']]
            transition_check = self.validate_transition(new_state, msg)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_enter_control_command: %s" % e.args) 
            print("DMCS unable to process_enter_control_command: %s" % e.args) 
            raise L1Error("DMCS unable to process_enter_control_command: %s" % e.args) 


    def process_start_command(self, msg):
        """ Pass the next state of the message transition (retrived from toolsmod.py)
            into validate_transition.

            :params msg: The message to be processed.

            :return: None.
        """
        try: 
            new_state = toolsmod.next_state[msg['MSG_TYPE']]
            transition_check = self.validate_transition(new_state, msg)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_start_command: %s" % e.args) 
            print("DMCS unable to process_start_command: %s" % e.args) 
            raise L1Error("DMCS unable to process_start_command: %s" % e.args) 


    def process_standby_command(self, msg):
        """ Pass the next state of the message transition (retrived from toolsmod.py)
            into validate_transition. If state transition is valid, create a new session
            id and send a 'NEW_SESSION' message.

            :params msg: The message to be processed.

            :return: None.
        """
        try: 
            new_state = toolsmod.next_state[msg['MSG_TYPE']]
            transition_check = self.validate_transition(new_state, msg)

            if transition_check:
                # send new session id to all
                session_id = self.INCR_SCBD.get_next_session_id()
                self.STATE_SCBD.set_current_session(session_id)
                self.STATE_SCBD.set_rafts_for_current_session(session_id)
                self.send_new_session_msg(session_id)
        except L1RedisError as e: 
            LOGGER.error("DMCS unable to process_standby_command - No redis connection: %s" % e.args) 
            print("DMCS unable to process_standby_command - No redis connection: %s" % e.args) 
            raise L1Error("DMCS unable to process_standby_command - No redis connection: %s" % e.args) 
        except Exception as e: 
            LOGGER.error("DMCS unable to process_standby_command: %s" % e.args) 
            print("DMCS unable to process_standby_command: %s" % e.args) 
            raise L1Error("DMCS unable to process_standby_command: %s" % e.args) 

    def process_disable_command(self, msg):
        """ Pass the next state of the message transition (retrived from toolsmod.py)
            into validate_transition.

            :params msg: The message to be processed.

            :return: None.
        """
        try: 
            new_state = toolsmod.next_state[msg['MSG_TYPE']]
            transition_check = self.validate_transition(new_state, msg)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_disable_command: %s" % e.args) 
            print("DMCS unable to process_disable_command: %s" % e.args) 
            raise L1Error("DMCS unable to process_disable_command: %s" % e.args) 


    def process_enable_command(self, msg):
        """ Pass the next state of the message transition (retrived from toolsmod.py)
            into validate_transition.

            :params msg: The message to be processed.

            :return: None.
        """
        try: 
            new_state = toolsmod.next_state[msg['MSG_TYPE']]
            transition_check = self.validate_transition(new_state, msg)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_disable_command: %s" % e.args) 
            print("DMCS unable to process_disable_command: %s" % e.args) 
            raise L1Error("DMCS unable to process_disable_command: %s" % e.args) 


    def process_set_value_command(self, msg):
        """ Generate ack message with value from passed in message and publish to
            OCS Bridge. Send an error message (ack_bool = false) if current state
            isn't ENABLE or message's value is invalid.

            :params msg: The message to be processed.

            :return: None.
        """
        try: 
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
        except L1RedisError as e: 
            LOGGER.error("DMCS unable to process_set_value_command - No redis connection: %s" % e.args) 
            print("DMCS unable to process_set_value_command - No redis connection: %s" % e.args) 
            raise L1Error("DMCS unable to process_set_value_command - No redis connection: %s" % e.args) 
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to process_set_value_command - No rabbit connection: %s" % e.args) 
            print("DMCS unable to process_set_value_command - No rabbit connection: %s" % e.args) 
            raise L1Error("DMCS unable to process_set_value_command - No rabbit connection: %s" % e.args) 
        except Exception as e: 
            LOGGER.error("DMCS unable to process_set_value_command: %s" % e.args) 
            print("DMCS unable to process_set_value_command: %s" % e.args) 
            raise L1Error("DMCS unable to process_set_value_command: %s" % e.args) 



    def process_exit_control_command(self, msg):
        """ Pass the next state of the message transition (retrived from toolsmod.py)
            into validate_transition.

            :params msg: The message to be processed.

            :return: None.
        """
        try: 
            new_state = toolsmod.next_state[msg['MSG_TYPE']]
            transition_check = self.validate_transition(new_state, msg)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_exit_control_command: %s" % e.args) 
            print("DMCS unable to process_exit_control_command: %s" % e.args) 
            raise L1Error("DMCS unable to process_exit_control_command: %s" % e.args) 


    def process_abort_command(self, msg):
        """ Pass the next state of the message transition (retrived from toolsmod.py)
            into validate_transition.

            :params msg: The message to be processed.

            :return: None.
        """
        try:
            new_state = toolsmod.next_state[msg['MSG_TYPE']]
            # Send out ABORT messages!!!
            transition_check = self.validate_transition(new_state, msg)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_abort_command: %s" % e.args) 
            print("DMCS unable to process_abort_command: %s" % e.args) 
            raise L1Error("DMCS unable to process_abort_command: %s" % e.args) 


    def process_stop_command(self, msg):
        """ Pass the next state of the message transition (retrived from toolsmod.py)
            into validate_transition.

            :params msg: The message to be processed.

            :return: None.
        """
        try: 
            new_state = toolsmod.next_state[msg['MSG_TYPE']]
            transition_check = self.validate_transition(new_state, msg)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_stop_command: %s" % e.args) 
            print("DMCS unable to process_stop_command: %s" % e.args) 
            raise L1Error("DMCS unable to process_stop_command: %s" % e.args) 
            


    def process_next_visit_event(self, params):
        """ Send next visit info to any devices in enable state.
            Keep track of current Next Visit for each device.
            Wait for timeout and then check for each ack's response.

            :params params: Next visit info.

            :return: None.
        """
        try: 
            # First, get dict of devices in Enable state with their consume queues
            visit_id = params['VISIT_ID']
            self.STATE_SCBD.set_visit_id(visit_id)
            enabled_devices = self.STATE_SCBD.get_devices_by_state(ENABLE)
            LOGGER.debug("Enabled device list is:")
            LOGGER.debug(enabled_devices)
            session_id = self.STATE_SCBD.get_current_session()

            acks = []
            for k in list(enabled_devices.keys()):
                consume_queue = self.STATE_SCBD.get_device_consume_queue(enabled_devices[k])
                if self.DP:
                  print("Consume queue for device %s is %s" % (enabled_devices[k], consume_queue)) 
                ## FIXME - Must each enabled device use its own ack_id? Or
                ## can we use the same method for broadcasting Forwarder messages?  
                ack = self.INCR_SCBD.get_next_timed_ack_id(k + "_NEXT_VISIT_ACK")
                acks.append(ack)
                msg = {}
                msg[MSG_TYPE] = k + '_NEXT_VISIT'
                msg[ACK_ID] = ack
                msg['SESSION_ID'] = session_id
                msg[VISIT_ID] = params[VISIT_ID]
                msg[BORE_SIGHT] = params['BORE_SIGHT']
                msg['REPLY_QUEUE'] = "dmcs_ack_consume"
                LOGGER.debug("Sending next visit msg %s to %s at queue %s" % (msg, k, consume_queue))
                self._publisher.publish_message(consume_queue, msg)

            self.ack_timer(3)
            for a in acks:
                ack_responses = self.ACK_SCBD.get_components_for_timed_ack(a)

                if ack_responses != None:
                    responses = list(ack_responses.keys())
                    for response in responses:
                        if ack_responses[response]['ACK_BOOL'] == False:
                            # Mark this device as messed up...maybe enter fault.
                            pass 
                else:
                    #Enter a fault state, as no devices are responding
                    pass
        except L1RedisError as e: 
            LOGGER.error("DMCS unable to process_next_visit_event - No redis connection: %s" % e.args)
            print("DMCS unable to process_next_visit_event - No redis connection: %s" % e.args)
            raise L1Error("DMCS unable to process_next_visit_event - No redis connection: %s" % e.args)
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to process_next_visit_event - No rabbit connection: %s" % e.args)
            print("DMCS unable to process_next_visit_event - No rabbit connection: %s" % e.args)
            raise L1Error("DMCS unable to process_next_visit_event - No rabbit connection: %s" % e.args)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_next_visit_event: %s" % e.args)
            print("DMCS unable to process_next_visit_event: %s" % e.args)
            raise L1Error("DMCS unable to process_next_visit_event: %s" % e.args)
            
            


    def process_start_integration_event(self, params):
        """ Send start integration message to all enabled devices with details of job,
            including new job_num and image_id.
            Send pending_ack message to all enabled devices, expires in 5s.

            :params params: Provide image_id.

            :return: None.
        """
        try: 
            ## FIX - see temp hack below...
            ## CCD List will eventually be derived from config key. For now, using a list set in top of this class
            ccd_list = self.CCD_LIST
            msg_params = {}
            # visit_id and image_id msg_params *could* be set in one line, BUT: the values are needed again below...
            visit_id = self.STATE_SCBD.get_current_visit()
            msg_params[VISIT_ID] = visit_id
            image_id = params[IMAGE_ID]  # NOTE: Assumes same image_id for all devices readout
            msg_params[IMAGE_ID] = image_id
            msg_params['REPLY_QUEUE'] = 'dmcs_ack_consume'
            msg_params['CCD_LIST'] = ccd_list
            session_id = self.STATE_SCBD.get_current_session()
            msg_params['SESSION_ID'] = session_id


            enabled_devices = self.STATE_SCBD.get_devices_by_state('ENABLE')
            acks = []
            for k in list(enabled_devices.keys()):
                ack_id = self.INCR_SCBD.get_next_timed_ack_id( str(k) + "_START_INT_ACK")
                acks.append(ack_id)
                job_num = self.INCR_SCBD.get_next_job_num( "job_" + session_id)
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
        except L1RedisError as e: 
            LOGGER.error("DMCS unable to process_start_integration_event - No redis connection: %s" % e.args)
            print("DMCS unable to process_start_integration_event - No redis connection: %s" % e.args)
            raise L1Error("DMCS unable to process_start_integration_event - No redis connection: %s" % e.args)
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to process_start_integration_event - No rabbit connection: %s" % e.args)
            print("DMCS unable to process_start_integration_event - No rabbit connection: %s" % e.args)
            raise L1Error("DMCS unable to process_start_integration_event - No rabbit connection: %s" % e.args)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_start_integration_event: %s" % e.args)
            print("DMCS unable to process_start_integration_event: %s" % e.args)
            raise L1Error("DMCS unable to process_start_integration_event: %s" % e.args)

 
    def process_at_start_integration_event(self, params):
        """ Send start integration message to all enabled devices with details of job,
            including new job_num and image_id.
            Send pending_ack message to all enabled devices, expires in 5s.

            :params params: Provide image_id.

            :return: None.
        """
        x = self.STATE_SCBD.at_device_is_enabled()
        print("MY OH MY -- x value to determine if AT is enabled is set to: %s" % x)
        if self.STATE_SCBD.at_device_is_enabled():
            LOGGER.debug("In process_at_start_integration_event, msg is: %s" % params)
            raft_ccd_list = []
            ccds = []
            ccds.append(self.wfs_ccd)
            raft_ccd_list.append(ccds)
            raft_list = []
            raft_list.append(self.wfs_raft)
            image_id = params[IMAGE_ID]
            msg_params = {}
            msg_params[MSG_TYPE] = 'AT_START_INTEGRATION'
            msg_params['IMAGE_ID'] = image_id
            msg_params['IMAGE_INDEX'] = params['IMAGE_INDEX']
            msg_params['IMAGE_SEQUENCE_NAME'] = params['IMAGE_SEQUENCE_NAME']
            msg_params['IMAGES_IN_SEQUENCE'] = params['IMAGES_IN_SEQUENCE']
            session_id = self.STATE_SCBD.get_current_session()
            msg_params['SESSION_ID'] = session_id
            msg_params['REPLY_QUEUE'] = 'dmcs_ack_consume'
            msg_params['RAFT_LIST'] = raft_list
            msg_params['RAFT_CCD_LIST'] = raft_ccd_list
    
            acks = []
            ack_id = self.INCR_SCBD.get_next_timed_ack_id( "AT_START_INT_ACK")
            acks.append(ack_id)
            job_num = self.INCR_SCBD.get_next_job_num( session_id)
            self.STATE_SCBD.add_job(job_num, image_id, "visit_0", raft_ccd_list)
            self.STATE_SCBD.set_value_for_job(job_num, 'DEVICE', "AT")
            self.STATE_SCBD.set_current_device_job(job_num, "AT")
            self.STATE_SCBD.set_job_state(job_num, "DISPATCHED")
            msg_params[JOB_NUM] = job_num
            msg_params[ACK_ID] = ack_id
            rkey = self.STATE_SCBD.get_device_consume_queue('AT')
            self._publisher.publish_message(rkey, msg_params)
    
            #### FIX replace non-pending acks with regular ack timer
            wait_time = 5  # seconds...
            self.set_pending_nonblock_acks(acks, wait_time)
        else:
            LOGGER.debug("Big Trouble in Little China - start_int msg for AT, but it is not enabled!")


    def process_readout_event(self, params):
        """ Send readout message to all enabled devices with details of job, including
            new job_num and image_id.
            Send pending_ack message to all enabled devices, expires in 5s.

            :params params: Provide image_id.

            :return: None.
        """
        try: 
            ccd_list = self.CCD_LIST

            msg_params = {}
            msg_params[VISIT_ID] = self.STATE_SCBD.get_current_visit()
            msg_params[IMAGE_ID] = params[IMAGE_ID]  # NOTE: Assumes same image_id for all devices readout
            msg_params['REPLY_QUEUE'] = 'dmcs_ack_consume'
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
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to process_readout_event - No rabbit connection: %s" % e.args)
            print("DMCS unable to process_readout_event - No rabbit connection: %s" % e.args)
            raise L1Error("DMCS unable to process_readout_event - No rabbit connection: %s" % e.args)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_readout_event: %s" % e.args)
            print("DMCS unable to process_readout_event: %s" % e.args)
            raise L1Error("DMCS unable to process_readout_event: %s" % e.args)
        # add in two additional acks for format and transfer complete


    def process_at_end_readout(self, params):
        """ Send readout message to all enabled devices with details of job, including
            new job_num and image_id.
            Send pending_ack message to all enabled devices, expires in 5s.

            :params params: Provide image_id.

            :return: None.
        """
        try: 
            msg_params = {}
            msg_params[MSG_TYPE] = 'AT_END_READOUT'
            msg_params[IMAGE_ID] = params[IMAGE_ID]  
            msg_params['IMAGE_INDEX'] = params['IMAGE_INDEX']  
            msg_params['IMAGE_SEQUENCE_NAME'] = params['IMAGE_SEQUENCE_NAME']  
            msg_params['IMAGES_IN_SEQUENCE'] = params['IMAGES_IN_SEQUENCE']  
            msg_params['REPLY_QUEUE'] = 'dmcs_ack_consume'
            session_id = self.STATE_SCBD.get_current_session()
            msg_params['SESSION_ID'] = session_id

            acks = []
            ack_id = self.INCR_SCBD.get_next_timed_ack_id("AT_END_READOUT_ACK")
            acks.append(ack_id)
            msg_params[ACK_ID] = ack_id
            job_num = self.STATE_SCBD.get_current_device_job('AT')
            msg_params[JOB_NUM] = job_num
            self.STATE_SCBD.set_job_state(job_num, "READOUT")
            rkey = self.STATE_SCBD.get_device_consume_queue('AT')
            LOGGER.info("Publishing end readout to: %s" % rkey) 
            LOGGER.debug("Publishing end readout message %s to: %s" % (pformat(msg_params), rkey))
            self._publisher.publish_message(rkey, msg_params)


            wait_time = 5  # seconds...
            self.set_pending_nonblock_acks(acks, wait_time)
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to process_readout_event - No rabbit connection: %s" % e.args)
            print("DMCS unable to process_readout_event - No rabbit connection: %s" % e.args)
            raise L1Error("DMCS unable to process_readout_event - No rabbit connection: %s" % e.args)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_readout_event: %s" % e.args)
            print("DMCS unable to process_readout_event: %s" % e.args)
            raise L1Error("DMCS unable to process_readout_event: %s" % e.args)
        # add in two additional acks for format and transfer complete

    def process_target_visit_event(self, params):
        try:
            msg = {}
            acks = []
            # First, get dict of devices in Enable state with their consume queues
            session_id = self.STATE_SCBD.get_current_session()
            msg['SESSION_ID'] = session_id
            visit_id = params['TARGET_ID']
            self.STATE_SCBD.set_visit_id(visit_id)
            msg['VISIT_ID'] = visit_id
            msg['RA'] = params['RA']
            msg['DEC'] = params['DEC']
            msg['ANGLE'] = params['ANGLE']
            raft_list, raft_ccd_list = self.STATE_SCBD.get_rafts_for_current_session_as_lists()
            msg['RAFT_LIST'] = raft_list
            msg['RAFT_CCD_LIST'] = raft_ccd_list
            #filter = params['FILTER']
            msg['REPLY_QUEUE'] = "dmcs_ack_consume"


            enabled_devices = self.STATE_SCBD.get_devices_by_state(ENABLE)
            LOGGER.debug("Enabled device list for %s is:" % visit_id)
            LOGGER.debug(enabled_devices)

            for k in list(enabled_devices.keys()):
                msg[MSG_TYPE] = k + '_NEXT_VISIT'
                ack_id = self.get_next_timed_ack_id( str(k) + "_NEXT_VISIT_ACK")
                acks.append(ack_id)
                msg[ACK_ID] = ack_id
                job_num = self.STATE_SCBD.get_next_job_num( session_id)
                self.STATE_SCBD.add_job(job_num, visit_id, raft_list, raft_ccd_list)
                #self.STATE_SCBD.set_value_for_job(job_num, 'FILTER', filter)
                self.STATE_SCBD.set_current_device_job(job_num, str(k))
                self.STATE_SCBD.set_job_state(job_num, "DISPATCHED")
                msg[JOB_NUM] = job_num

                consume_queue = self.STATE_SCBD.get_device_consume_queue(k)
                LOGGER.debug("Sending next visit msg %s to %s at queue %s" % (msg, k, consume_queue))
                self._publisher.publish_message(consume_queue, msg)

            ## FIX - Use different type of ack here...
            self.ack_timer(3)
            for a in acks:
                ack_responses = self.ACK_SCBD.get_components_for_timed_ack(a)

                if ack_responses != None:
                    responses = list(ack_responses.keys())
                    for response in responses:
                        if ack_responses[response]['ACK_BOOL'] == False:
                            # Mark this device as messed up...maybe enter fault.
                            pass
                else:
                    #Enter a fault state, as no devices are responding
                    pass
        except L1RedisError as e:
            LOGGER.error("DMCS unable to process_next_visit_event - No redis connection: %s" % e.args)
            print("DMCS unable to process_next_visit_event - No redis connection: %s" % e.args)
            raise L1Error("DMCS unable to process_next_visit_event - No redis connection: %s" % e.args)
        except L1RabbitConnectionError as e:
            LOGGER.error("DMCS unable to process_next_visit_event - No rabbit connection: %s" % e.args)
            print("DMCS unable to process_next_visit_event - No rabbit connection: %s" % e.args)
            raise L1Error("DMCS unable to process_next_visit_event - No rabbit connection: %s" % e.args)
        except Exception as e:
            LOGGER.error("DMCS unable to process_next_visit_event: %s" % e.args)
            print("DMCS unable to process_next_visit_event: %s" % e.args)
            raise L1Error("DMCS unable to process_next_visit_event: %s" % e.args)



    def process_ccs_take_images_event(self, params):  
        try:
            msg = {}
            num_images = params['NUM_IMAGES']
            msg['NUM_IMAGES'] = num_images
            enabled_devices = self.STATE_SCBD.get_devices_by_state('ENABLE')
            for k in list(enabled_devices.keys()):
                msg[MSG_TYPE] = str(k) + '_TAKE_IMAGES'
                job_num = self.STATE_SCBD.get_current_device_job(k)
                msg[JOB_NUM] = job_num
                self.STATE_SCBD.set_value_for_job(job_num, self.EXPECTED_NUM_IMAGES, num_images)
                self.STATE_SCBD.set_job_state(job_num, "TAKE_IMAGES")
                self._publisher.publish_message(self.STATE_SCBD.get_device_consume_queue(k), msg)

        except L1RedisError as e:
            LOGGER.error("DMCS unable to process_ccs_take_images_event - No redis connection: %s" % e.args)
            print("DMCS unable to process_start_integration_event - No redis connection: %s" % e.args)
            raise L1Error("DMCS unable to process_start_integration_event - No redis connection: %s" % e.args)
        except Exception as e:
            LOGGER.error("DMCS unable to process_ccs_take_images_event: %s" % e.args)
            print("DMCS unable to process_ccs_take_images_event: %s" % e.args)
            raise L1Error("DMCS unable to process_ccs_take_images_event: %s" % e.args)



    ### This method receives the all important image name message parameter in params.
    def process_end_readout(self, params):
        try:
            msg_params = {}
            msg_params[VISIT_ID] = self.STATE_SCBD.get_current_visit()
            msg_params[IMAGE_ID] = params[IMAGE_ID]  # NOTE: Assumes same image_id for all devices readout
            msg_params['REPLY_QUEUE'] = 'dmcs_ack_consume'
            session_id = self.STATE_SCBD.get_current_session()
            msg_params['SESSION_ID'] = session_id

            enabled_devices = self.STATE_SCBD.get_devices_by_state('ENABLE')
            acks = []
            for k in list(enabled_devices.keys()):
                ack_id = self.INCR_SCBD.get_next_timed_ack_id( str(k) + "_END_READOUT_ACK")
                acks.append(ack_id)
                job_num = self.STATE_SCBD.get_current_device_job(str(k))
                msg_params[MSG_TYPE] = k + '_END_READOUT'
                msg_params[ACK_ID] = ack_id
                msg_params[JOB_NUM] = job_num
                self.STATE_SCBD.set_job_state(job_num, "READOUT")
                self._publisher.publish_message(self.STATE_SCBD.get_device_consume_queue(k), msg_params)


            wait_time = 5  # seconds...
            self.set_pending_nonblock_acks(acks, wait_time)
        except L1RabbitConnectionError as e:
            LOGGER.error("DMCS unable to process_readout_event - No rabbit connection: %s" % e.args)
            print("DMCS unable to process_readout_event - No rabbit connection: %s" % e.args)
            raise L1Error("DMCS unable to process_readout_event - No rabbit connection: %s" % e.args)
        except Exception as e:
            LOGGER.error("DMCS unable to process_readout_event: %s" % e.args)
            print("DMCS unable to process_readout_event: %s" % e.args)
            raise L1Error("DMCS unable to process_readout_event: %s" % e.args)
        # add in two additional acks for format and transfer complete


    def process_take_images_done(self, params):
        msg_params = {}
        msg_params[MSG_TYPE] = 'AR_TAKE_IMAGES_DONE'
        enabled_devices = self.STATE_SCBD.get_devices_by_state('ENABLE')
        acks = []
        for k in list(enabled_devices.keys()):
            ack_id = self.get_next_timed_ack_id( str(k) + "_TAKE_IMAGES_DONE_ACK")
            acks.append(ack_id)
            job_num = self.STATE_SCBD.get_current_device_job(str(k))
            msg_params[MSG_TYPE] = k + '_TAKE_IMAGES_DONE'
            msg_params[ACK_ID] = ack_id
            msg_params[JOB_NUM] = job_num
            msg_params["REPLY_QUEUE"] = "ar_foreman_ack_publish"
            self.STATE_SCBD.set_job_state(job_num, "READOUT")
            self._publisher.publish_message(self.STATE_SCBD.get_device_consume_queue(k), msg_params)

        ### FIX Progressive timer, then collect acks and process what was done, then return to DMCS with results

    def process_header_ready_event(self, params):
        msg_params = {}
        fname = params['FILENAME']        
        msg_params['FILENAME'] = self.efd + fname        
        enabled_devices = self.STATE_SCBD.get_devices_by_state('ENABLE')
        for k in list(enabled_devices.keys()):
            msg_params[MSG_TYPE] = k + '_HEADER_READY'
            msg_params["REPLY_QUEUE"] = "ar_foreman_ack_publish"
            job_num = self.STATE_SCBD.get_current_device_job(str(k))
            msg_params[JOB_NUM] = job_num
            self.STATE_SCBD.set_job_state(job_num, "READOUT")
            self._publisher.publish_message(self.STATE_SCBD.get_device_consume_queue(k), msg_params)


    def process_at_header_ready_event(self, params):
        ack_id = self.get_next_timed_ack_id( 'AT_HEADER_READY_ACK')
        msg_params = {}
        fname = params['FILENAME']        
        msg_params['FILENAME'] = fname        
        msg_params[MSG_TYPE] = 'AT_HEADER_READY'
        msg_params[IMAGE_ID] = params[IMAGE_ID]  
        msg_params["REPLY_QUEUE"] = "at_foreman_ack_publish"
        msg_params[ACK_ID] = ack_id
        job_num = self.STATE_SCBD.get_current_device_job('AT')
        self.STATE_SCBD.set_job_state(job_num, "HEADER_READY")
        self._publisher.publish_message(self.STATE_SCBD.get_device_consume_queue('AT'), msg_params)


    def process_fault(self, params):
        device = params['DEVICE']
        fault_type = params['FAULT_TYPE']
        error_code = params['ERROR_CODE']
        if fault_type == 'FAULT':
            self.set_device_to_fault_state(device, params['ERROR_CODE'])
            LOGGER.error("DMCS seeing a FAULT state from %s device with error code: %s" % (device, error_code))
            LOGGER.error("Description string is:  %s." % params['DESCRIPTION'])
        else:
            LOGGER.critical("DMCS seeing a %s state from %s device...error code is %s and description is %s" % \
                 (device, fault_type, error_code, params['DESCRIPTION']))

        msg_params = {}
        msg_params[MSG_TYPE] = FAULT
        msg_params['COMPONENT'] = params['COMPONENT']
        msg_params['DEVICE'] = device 
        msg_params['ERROR_CODE'] = error_code
        msg_params['FAULT_TYPE'] = fault_type
        msg_params['DESCRIPTION'] = params['DESCRIPTION']
        self._publisher.publish_message(self.DMCS_OCS_PUBLISH, msg_params)


    def set_device_to_fault_state(self, device, params):
        # set state to FAULT for device
        # associate err_code with fault
        # There should be a 'Fault_History' list that yaml dumps all params of the fault and assoiates it with
        #a date
        self.STATE_SCBD.set_device_state(device, FAULT)
        self.STATE_SCBD.append_new_fault_to_fault_history(params)


    def process_ack(self, params):
        """ Add new ack message to AckScoreboard. 

            :params params: Ack message.

            :return: None.
        """
        try: 
            self.ACK_SCBD.add_timed_ack(params)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_ack: %s" % e.args)
            print("DMCS unable to process_ack: %s" % e.args)
            raise L1Error("DMCS unable to process_ack: %s" % e.args)
            


    def process_pending_ack(self, params):
        """ Store pending_ack message in AckScoreboard.

            :params params: pending_ck message.

            :return: None.
        """
        try: 
            self.ACK_SCBD.add_pending_nonblock_ack(params)
        except Exception as e: 
            LOGGER.error("DMCS unable to process_pending_ack: %s" % e.args)
            print("DMCS unable to process_pending_ack: %s" % e.args)
            raise L1Error("DMCS unable to process_pending_ack: %s" % e.args)
            


    def process_readout_results_ack(params):
        """ Mark job_num as COMPLETE and store its results.
            Add CCDs to Backlog Scoreboard if any failed to be transferred.

            :params params: readout_results message to be processed.

            :return: None.
        """
        try: 
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
        except Exception as e: 
            LOGGER.error("DMCS unable to process_readout_results_ack: %s" % e.args) 
            print("DMCS unable to process_readout_results_ack: %s" % e.args) 
            raise L1Error("DMCS unable to process_readout_results_ack: %s" % e.args) 


    def get_backlog_stats(self):
        """ Return brief info on all backlog items.

            :params: None.

            :return: None.
        """
        pass

    def get_backlog_details(self):
        """ Return detailed dictionary of all backlog items and the nature of each.

            :params: None.

            :return: None.
        """
        pass

    def get_next_backlog_item(self):
        """ This method will return a backlog item according to a policy in place.

            :params: None.

            :return: None.
        """
        pass


    def send_new_session_msg(self, session_id):
        """ Send a new mession message to all devices.
            Send pending_ack message to all devices, expires in 3s.

            :params session_id: New session id to be processed.

            :return: None.
        """

        try: 
            ack_ids = [] 
            msg = {}
            #msg['MSG_TYPE'] = 'NEW_SESSION'
            msg['REPLY_QUEUE'] = "dmcs_ack_consume"
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
        except Exception as e: 
            LOGGER.error("DMCS unable to send_new_seesion_msg: %s" % e.args) 
            print("DMCS unable to send_new_seesion_msg: %s" % e.args) 
            raise L1Error("DMCS unable to send_new_seesion_msg: %s" % e.args) 


    def validate_transition(self, new_state, msg_in):
        """ Check if state transition is valid.

            For message with type START: if cfg key is valid, call StateScoreboard
            to set device cfg key; if not, send error message to OCS Bridge.

            For other type of message: if transition is valid, set device state in
            StateScoreboard and send message to OCS Bridge; if not, send error message
            to OCS Bridge.

            :params new_state: State to transition to.
            :params msg_in: Message to be processed.

            :return transition_is_valid: If the transition is valid.
        """
        try: 
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
        except Exception as e: 
            LOGGER.error("DMCS unable to validate_transaction - can't use cfgkey: %s" % e.args) 
            print("DMCS unable to validate_transaction - can't use cfgkey: %s" % e.args) 
            raise L1Error("DMCS unable to validate_transaction - can't use cfgkey") 
        

        try: 
            transition_is_valid = toolsmod.state_matrix[current_index][new_index]
            if transition_is_valid == True:
                self.STATE_SCBD.set_device_state(device, new_state)
                response = str(device) + " device in " + new_state
                response = response + cfg_response
                self.send_ocs_ack(transition_is_valid, response, msg_in)
            else:
                LOGGER.error("DMCS - BAD Device Transition from %s  to %s" % (current_state, new_state))
                print("DMCS - BAD Device Transition from %s  to %s" % (current_state, new_state))
                response = "Invalid transition: " + str(current_state) + " to " + new_state
                #response = response + ". Device remaining in " + current_state + " state."
                self.send_ocs_ack(transition_is_valid, response, msg_in)
        except Exception as e: 
            LOGGER.error("DMCS unable to validate_transaction - can't check scoreboards: %s" % e.args) 
            print("DMCS unable to validate_transaction - can't check scoreboards: %s" % e.args) 
            raise L1Error("DMCS unable to validate_transaction - can't check scoreboards: %s" % e.args) 
            

        return transition_is_valid
 

    def set_pending_nonblock_acks(self, acks, wait_time):
        """ Send pending_ack message to dmcs_ack_comsume queue with wait_time as
            expiry_time.

            :params acks: List of ack_id to send pending_ack message to.
            :params wait_time: expiry_time in seconds.

            :return: None.
        """
        try: 
            start_time = datetime.datetime.now().time()
            expiry_time = self.add_seconds(start_time, wait_time)
            ack_msg = {}
            ack_msg[MSG_TYPE] = 'PENDING_ACK'
            ack_msg['EXPIRY_TIME'] = expiry_time
            for ack in acks:
                ack_msg[ACK_ID] = ack
                self._publisher.publish_message("dmcs_ack_consume", ack_msg)
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to send_pending_nonblock_acks: %s" % e.args)
            print("DMCS unable to send_pending_nonblock_acks: %s" % e.args)
            raise L1Error("DMCS unable to send_pending_nonblock_acks: %s" % e.args) 
        except Exception as e: 
            LOGGER.error("DMCS unable to send_pending_nonblock_acks: %s" % e.args)
            print("DMCS unable to send_pending_nonblock_acks: %s" % e.args) 
            raise L1Error("DMCS unable to send_pending_nonblock_acks: %s" % e.args)
        


    def send_ocs_ack(self, transition_check, response, msg_in):
        """ Send ack message to OCS Bridge.

            If transition is valid, call send_appropriate_events_by_state to update
            and publish new state of device.

            :params transition_check: If transition is valid.
            :params response: String, appropriate response for the transition.
            :params msg_in: Message to be processed.

            :return: None.
        """
        try: 
            message = {}
            message['MSG_TYPE'] = msg_in['MSG_TYPE'] + "_ACK"
            message['DEVICE'] = msg_in['DEVICE']
            message['ACK_ID'] = msg_in['ACK_ID']
            message['CMD_ID'] = msg_in['CMD_ID']
            message['ACK_BOOL'] = transition_check
            message['ACK_STATEMENT'] = response
            self._publisher.publish_message(self.DMCS_OCS_PUBLISH, message) 
        except L1RabbitConnnectionError as e: 
            LOGGER.error("DMCS unable to send_ocs_ack: %s" % e.args) 
            print("DMCS unable to send_ocs_ack: %s" % e.args) 
            raise L1Error("DMCS unable to send_ocs_ack: %s" % e.args) 
        except Exception as e: 
            LOGGER.error("DMCS unable to send_ocs_ack: %s" % e.args) 
            print("DMCS unable to send_ocs_ack: %s" % e.args)
            raise L1Error("DMCS unable to send_ocs_ack - Rabbit Problem?: %s" % e.args)

        if transition_check:
            self.send_appropriate_events_by_state(msg_in['DEVICE'], msg_in['MSG_TYPE'])


    def send_appropriate_events_by_state(self, dev, transition):
        """ Send appropriate messages of state transition for device to OCS Bridge.

            :params dev: Device with state change.
            :params transition: Next state for device.

            :return: None.
        """
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
        """ Send SUMMARY_STATE_EVENT message of device with its current state to OCS Bridge.

            :params device: Device with state change.

            :return: None.
        """
        try: 
            message = {}
            message[MSG_TYPE] = 'SUMMARY_STATE_EVENT'
            message['DEVICE'] = device
            message['CURRENT_STATE'] = toolsmod.summary_state_enum[self.STATE_SCBD.get_device_state(device)]
            self._publisher.publish_message(self.DMCS_OCS_PUBLISH, message)
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to send_summary_state_event: %s" % e.args)
            print("DMCS unable to send_summary_state_event: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 11)
        except Exception as e: 
            LOGGER.error("DMCS unable to send_summary_state_event: %s" % e.args)
            print("DMCS unable to send_summary_state_event: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 10)


    def send_recommended_setting_versions_event(self, device):
        """ Send RECOMMENDED_SETTINGS_VERSION_EVENT message of device with its list of cfg keys to
            OCS Bridge.

            :params device: Device with state change.

            :return: None.
        """
        try: 
            message = {}
            message[MSG_TYPE] = 'RECOMMENDED_SETTINGS_VERSION_EVENT'
            message['DEVICE'] = device
            message['CFG_KEY'] = self.STATE_SCBD.get_device_cfg_key(device)
            self._publisher.publish_message(self.DMCS_OCS_PUBLISH, message)
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to send_recommended_settings_version_event: %s" % e.args)
            print("DMCS unable to send_recommended_settings_version_event: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 11)
        except Exception as e: 
            LOGGER.error("DMCS unable to send_recommended_settings_version_event: %s" % e.args)
            print("DMCS unable to send_recommended_settings_version_event: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 10)


    def send_setting_applied_event(self, device):
        """ Send SETTINGS_APPLIED_EVENT message of device to OCS Bridge.

            :params device: Device with state change.

            :return: None.
        """
        try: 
            message = {}
            message[MSG_TYPE] = 'SETTINGS_APPLIED_EVENT'
            message['DEVICE'] = device
            message['APPLIED'] = True
            self._publisher.publish_message(self.DMCS_OCS_PUBLISH, message)
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to send_setting_applied_event: %s" % e.args)
            print("DMCS unable to send_setting_applied_event: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 11)
        except Exception as e: 
            LOGGER.error("DMCS unable to send_setting_applied_event: %s" % e.args)
            print("DMCS unable to send_setting_applied_event: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 10)
        


    def send_applied_setting_match_start_event(self, device):
        """ Send APPLIED_SETTINGS_MATCH_START_EVENT message of device to OCS Bridge.

            :params device: Device with state change.

            :return: None.
        """
        try: 
            message = {}
            message[MSG_TYPE] = 'APPLIED_SETTINGS_MATCH_START_EVENT'
            message['DEVICE'] = device
            message['APPLIED'] = True
            self._publisher.publish_message(self.DMCS_OCS_PUBLISH, message)
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to send_applied_setting_match_start_event: %s" % e.args)
            print("DMCS unable to send_applied_setting_match_start_event: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 11)
        except Exception as e: 
            LOGGER.error("DMCS unable to send_applied_setting_match_start_event: %s" % e.args)
            print("DMCS unable to send_applied_setting_match_start_event: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 10)


    def send_error_code_event(self, device):
        """ Send ERROR_CODE_EVENT message of device with error code 102 to OCS Bridge.

            :params device: Device with state change.

            :return: None.
        """
        try: 
            message = {}
            message[MSG_TYPE] = 'ERROR_CODE_EVENT'
            message['DEVICE'] = device
            message['ERROR_CODE'] = 102
            self._publisher.publish_message(self.DMCS_OCS_PUBLISH, message)
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to send_error_code_event: %s" % e.args)
            print("DMCS unable to send_error_code_event: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 11)
        except Exception as e: 
            LOGGER.error("DMCS unable to send_error_code_event: %s" % e.args)
            print("DMCS unable to send_error_code_event: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 10)
        

    def get_next_timed_ack_id(self, ack):
        """ Increment ack by 1, and persist latest value between starts.
            Return ack id merged with ack type string.

            :params ack_type: Description of ack.

            :return retval: String with ack type followed by next ack id.
        """
        try: 
            new_val = self.INCR_SCBD.get_next_timed_ack_id(ack)
        except Exception as e: 
            LOGGER.error("DMCS unable to get_next_timed_ack_id: %s" % e.args)
            print("DMCS unable to get_next_timed_ack_id: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 3); 

        return new_val 


    def ack_timer(self, seconds):
        """ Sleeps for user-defined seconds.

            :params seconds: Time to sleep in seconds.

            :return: True.
        """
        sleep(seconds)
        return True


    def progressive_ack_timer(self, ack_id, expected_replies, seconds):
        """ Sleeps for user-defined seconds, or less if everyone has reported back in.

            :params ack_id: Ack ID to wait for.

            :params expected_replies: Number of components expected to ack..

            :params seconds: Maximum time to wait in seconds.

            :return: The dictionary that represents the responses from the components ack'ing.
                     Note: If only one component will ack, this method breaks out of its
                           loop after the one ack shows up - effectively beating the maximum
                           wait time.
        """
        counter = 0.0
        while (counter < seconds):
            counter = counter + 0.5
            sleep(0.5)
            response = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
            if response == None:
                continue
            if len(list(response.keys())) == expected_replies:
                return response

        ## Try one final time
        response = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
        if response == None:
            return None
        elif len(list(response.keys())) == expected_replies:
            return response
        else:
            return None


    def extract_config_values(self):
        LOGGER.info('Reading YAML Config file %s' % self._config_file)
        try:
            cdm = toolsmod.intake_yaml_file(self._config_file)
        except IOError as e:
            LOGGER.critical("Unable to find CFG Yaml file %s\n" % self._config_file)
            sys.exit(101) 

        try:
            self._msg_name = cdm[ROOT]['DMCS_BROKER_NAME']      # Message broker user & passwd
            self._msg_passwd = cdm[ROOT]['DMCS_BROKER_PASSWD']
            self._pub_name = cdm[ROOT]['DMCS_BROKER_PUB_NAME']
            self._pub_passwd = cdm[ROOT]['DMCS_BROKER_PUB_PASSWD']
            self._pub_fault_name = cdm[ROOT]['DMCS_FAULT_PUB_NAME']
            self._pub_fault_passwd = cdm[ROOT]['DMCS_FAULT_PUB_PASSWD']
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self.ddict = cdm[ROOT]['FOREMAN_CONSUME_QUEUES']
            self.rdict = cdm[ROOT]['DEFAULT_RAFT_CONFIGURATION']
            self.state_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_STATE_SCBD']
            self.ack_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_ACK_SCBD']
            self.incr_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_INCR_SCBD']
            self.backlog_db_instance = cdm[ROOT]['SCOREBOARDS']['DMCS_BACKLOG_SCBD']
            self.CCD_LIST = cdm[ROOT]['CCD_LIST']
            self.ar_cfg_keys = cdm[ROOT]['AR_CFG_KEYS']
            self.pp_cfg_keys = cdm[ROOT]['PP_CFG_KEYS']
            self.cu_cfg_keys = cdm[ROOT]['CU_CFG_KEYS']
            self.at_cfg_keys = cdm[ROOT]['AT_CFG_KEYS']
            self.efd_login = cdm[ROOT]['EFD']['EFD_LOGIN']
            self.efd_ip = cdm[ROOT]['EFD']['EFD_IP']
            self.wfs_raft = cdm[ROOT]['ATS']['WFS_RAFT']
            self.wfs_ccd = cdm[ROOT]['ATS']['WFS_CCD']
            broker_vhost = cdm[ROOT]['BROKER_VHOST']
            queue_purges = cdm[ROOT]['QUEUE_PURGES']
            self.dmcs_ack_id_file = cdm[ROOT]['DMCS_ACK_ID_FILE']
            self.efd = self.efd_login + "@" + self.efd_ip + ":"
        except KeyError as e:
            trace = traceback.print_exc()
            emsg = "Unable to find key in CDM representation of %s\n" % filename
            LOGGER.critical(emsg + trace)
            sys.exit(102)

        return True



    def setup_consumer_threads(self):
        base_broker_url = "amqp://" + self._msg_name + ":" + \
                                            self._msg_passwd + "@" + \
                                            str(self._base_broker_addr)
        print("CONSUMER THREADS: %s" % base_broker_url)
        LOGGER.info('Building _base_broker_url. Result is %s', base_broker_url)

        self.shutdown_event = threading.Event()
        self.shutdown_event.clear()

        # Set up kwargs that describe consumers to be started
        # The DMCS needs two message consumers

        try: 
            kws = {}
            md = {}
            md['amqp_url'] = base_broker_url
            md['name'] = 'Thread-ocs_dmcs_consume'
            md['queue'] = 'ocs_dmcs_consume'
            md['callback'] = self.on_ocs_message
            md['format'] = "YAML"
            md['test_val'] = None
            kws[md['name']] = md

            md = {}
            md['amqp_url'] = base_broker_url
            md['name'] = 'Thread-dmcs_ack_consume'
            md['queue'] = 'dmcs_ack_consume'
            md['callback'] = self.on_ack_message
            md['format'] = "YAML"
            md['test_val'] = None
            kws[md['name']] = md

            md = {}
            md['amqp_url'] = base_broker_url
            md['name'] = 'Thread-dmcs_fault_consume'
            md['queue'] = 'dmcs_fault_consume'
            md['callback'] = self.on_fault_message
            md['format'] = "YAML"
            md['test_val'] = None
            kws[md['name']] = md

            self.thread_manager = ThreadManager('thread-manager', kws, self.shutdown_event)

        except ThreadError as e:
            LOGGER.error("DMCS unable to launch Consumers - Thread Error: %s" % e.args)
            print("DMCS unable to launch Consumers - Thread Error: %s" % e.args)
            raise L1ConsumerError("Thread problem preventing Consumer launch: %s" % e.args)
        except Exception as e: 
            LOGGER.error("DMCS unable to launch Consumers: %s" % e.args)
            print("DMCS unable to launch Consumers: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 1) 

        self.thread_manager.start()
         

    def setup_scoreboards(self):
        try: 
            LOGGER.info('Setting up DMCS Scoreboards')
            self.BACKLOG_SCBD = BacklogScoreboard('DMCS_BACKLOG_SCBD', self.backlog_db_instance)
            self.ACK_SCBD = AckScoreboard('DMCS_ACK_SCBD', self.ack_db_instance)
            self.INCR_SCBD = IncrScoreboard('DMCS_INCR_SCBD', self.incr_db_instance)
            self.STATE_SCBD = StateScoreboard('DMCS_STATE_SCBD', self.state_db_instance, self.ddict, self.rdict)
        except L1RabbitConnectionError as e: 
            LOGGER.error("DMCS unable to complete setup_scoreboards - No Rabbit Connect: %s" % e.args)
        except L1RedisError as e: 
            LOGGER.error("DMCS unable to complete setup_scoreboards - No Redis connect: %s" % e.args)
            print("DMCS unable to complete setup_scoreboards - No Redis connection: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 12)
        except Exception as e: 
            LOGGER.error("DMCS init unable to complete setup_scoreboards: %s" % e.args)
            print("DMCS unable to complete setup_scoreboards: %s" % e.args)
            sys.exit(self.ERROR_CODE_PREFIX + 10)

        try: 
            # All devices wake up in OFFLINE state
            self.STATE_SCBD.set_device_state("AR","OFFLINE")

            self.STATE_SCBD.set_device_state("PP","OFFLINE")

            self.STATE_SCBD.set_device_state("CU","OFFLINE")

            self.STATE_SCBD.set_device_state("AT","OFFLINE")

            self.STATE_SCBD.add_device_cfg_keys('AR', self.ar_cfg_keys)
            self.STATE_SCBD.set_device_cfg_key('AR',self.STATE_SCBD.get_cfg_from_cfgs('AR', 0))

            self.STATE_SCBD.add_device_cfg_keys('PP', self.pp_cfg_keys)
            self.STATE_SCBD.set_device_cfg_key('PP',self.STATE_SCBD.get_cfg_from_cfgs('PP', 0))

            self.STATE_SCBD.add_device_cfg_keys('CU', self.cu_cfg_keys)
            self.STATE_SCBD.set_device_cfg_key('CU',self.STATE_SCBD.get_cfg_from_cfgs('CU', 0))

            self.STATE_SCBD.add_device_cfg_keys('AT', self.at_cfg_keys)
            self.STATE_SCBD.set_device_cfg_key('AT',self.STATE_SCBD.get_cfg_from_cfgs('AT', 0))

            self.send_appropriate_events_by_state('AR', 'OFFLINE')
            self.send_appropriate_events_by_state('PP', 'OFFLINE')
            self.send_appropriate_events_by_state('CU', 'OFFLINE')
            self.send_appropriate_events_by_state('AT', 'OFFLINE')
        except Exception as e: 
            LOGGER.error("DMCS init unable to complete setup_scoreboards - Cannot set scoreboards: %s" % e.args)
            print("DMCS init unable to complete setup_scoreboards - Cannot set scoreboards: %s" % e.args) 
            sys.exit(self.ERROR_CODE_PREFIX + 10) 
        LOGGER.info('DMCS Scoreboard Init complete')


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

    def shutdown(self):
        LOGGER.info("Shutting down Consumer threads.")
        self.shutdown_event.set()
        LOGGER.debug("Thread Manager shutting down and app exiting...")
        #sys.exit(0)
        print("\n")
        os._exit(0)

    def dmcs_finalize(self):
        self.STATE_SCBD.scbd_finalize()


def main():
    logging.basicConfig(filename='logs/DMCS.log', level=logging.INFO, format=LOG_FORMAT)
    dmsc = DMCS()
    print("DMCS seems to be working")
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        x = os.getpid()
        print("Killing PID: %s" % x)
        call(["kill","-9",str(x)])
        pass

    print("")
    print("DMCS Done.")




if __name__ == "__main__": main()
