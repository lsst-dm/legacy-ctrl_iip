import toolsmod
from toolsmod import get_timestamp
import logging
import pprint
import pika
import redis
import yaml
import sys
import os
import time
import datetime
from time import sleep
import _thread
from const import *
from Scoreboard import Scoreboard
from ForwarderScoreboard import ForwarderScoreboard
from JobScoreboard import JobScoreboard
from AckScoreboard import AckScoreboard
from Consumer import Consumer
from SimplePublisher import SimplePublisher

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class PromptProcessDevice:
    PP_JOB_SCBD = None
    PP_FWD_SCBD = None
    PP_ACK_SCBD = None
    COMPONENT_NAME = 'PROMPT_PROCESS_FOREMAN'
    PP_FOREMAN_CONSUME = "pp_foreman_consume"
    PP_FOREMAN_ACK_PUBLISH = "pp_foreman_ack_publish"
    NCSA_PUBLISH = "ncsa_publish"
    NCSA_CONSUME = "ncsa_consume"
    FORWARDER_PUBLISH = "forwarder_publish"
    ACK_PUBLISH = "ack_publish"
    YAML = 'YAML'
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'direct'
    MAX_CCDS_PER_FWDR = 10


    def __init__(self, filename=None):
        toolsmod.singleton(self)

        self.pp = pprint.PrettyPrinter(indent=4)
        self._config_file = CFG_FILE
        if filename != None:
            self._config_file = filename

        try:
            cdm = toolsmod.intake_yaml_file(self._config_file)
        except IOError as e:
            trace = traceback.print_exc()
            emsg = "Unable to find CFG Yaml file %s\n" % self._config_file
            LOGGER.critical(emsg + trace)
            sys.exit(102)

        LOGGER.info('Extracting values from Config dictionary')
        self.extract_config_values(cdm)



        #if 'QUEUE_PURGES' in cdm[ROOT]:
        #    self.purge_broker(cdm['ROOT']['QUEUE_PURGES'])

        self._base_msg_format = self.YAML
        self._ncsa_msg_format = self.YAML

        if 'BASE_MSG_FORMAT' in cdm[ROOT]:
            self._base_msg_format = cdm[ROOT][BASE_MSG_FORMAT]

        if 'NCSA_MSG_FORMAT' in cdm[ROOT]:
            self._ncsa_msg_format = cdm[ROOT][NCSA_MSG_FORMAT]

        self._base_broker_url = 'amqp_url'
        self._ncsa_broker_url = 'amqp_url'
        self._next_timed_ack_id = 0


        # Create Redis Forwarder table with Forwarder info

        self.FWD_SCBD = ForwarderScoreboard('PP_FWD_SCBD', self._scbd_dict['PP_FWD_SCBD'], self.forwarder_dict)
        self.JOB_SCBD = JobScoreboard('PP_JOB_SCBD', self._scbd_dict['PP_JOB_SCBD'])
        self.ACK_SCBD = AckScoreboard('PP_ACK_SCBD', self._scbd_dict['PP_ACK_SCBD'])

        self._msg_actions = { 'NEW_SESSION': self.set_session,
                              'NEXT_VISIT': self.set_visit, 
                              'START_INTEGRATION': self.process_start_integration,
                              'READOUT': self.process_dmcs_readout,
                              'NCSA_RESOURCE_QUERY_ACK': self.process_ack,
                              'NCSA_START_INTEGRATION_ACK': self.process_ack,
                              'NCSA_READOUT_ACK': self.process_ack,
                              'FORWARDER_HEALTH_CHECK_ACK': self.process_ack,
                              'FORWARDER_JOB_PARAMS_ACK': self.process_ack,
                              'FORWARDER_READOUT_ACK': self.process_ack,
                              'PENDING_ACK': self.process_pending_ack,
                              'NEW_JOB_ACK': self.process_ack }


        # Build all necessary Broker connection URLs
        self._base_broker_url = "amqp://" + self._sub_name + ":" + \
                                            self._sub_passwd + "@" + \
                                            str(self._base_broker_addr)

        self._pub_base_broker_url = "amqp://" + self._pub_name + ":" + \
                                                self._pub_passwd + "@" + \
                                                str(self._base_broker_addr)

        self._ncsa_broker_url = "amqp://" + self._sub_ncsa_name + ":" + \
                                            self._sub_ncsa_passwd + "@" + \
                                            str(self._ncsa_broker_addr)

        self._pub_ncsa_broker_url = "amqp://" + self._pub_ncsa_name + ":" + \
                                                self._pub_ncsa_passwd + "@" + \
                                                str(self._ncsa_broker_addr)

        LOGGER.info('Building _base_broker_url. Result is %s', self._base_broker_url)
        LOGGER.info('Building _ncsa_broker_url. Result is %s', self._ncsa_broker_url)
        LOGGER.info('Setting up consumers on %s', self._base_broker_url)
        self.setup_publishers()
        self.setup_consumers()


    def setup_consumers(self):
        """This method sets up a message listener from each entity
           with which the BaseForeman has contact here. These
           listeners are instanced in this class, but their run
           methods are each called as a separate thread. While
           pika does not claim to be thread safe, the manner in which 
           the listeners are invoked below is a safe implementation
           that provides non-blocking, fully asynchronous messaging
           to the BaseForeman.

           The code in this file expects message bodies to arrive as
           YAML'd python dicts, while in fact, message bodies are sent
           on the wire as XML; this way message format can be validated,
           versioned, and specified in just one place. To make this work,
           there is an object that translates the params dict to XML, and
           visa versa. The translation object is instantiated by the consumer
           and acts as a filter before sending messages on to the registered
           callback for processing.

        """
        LOGGER.info('Running start_new_thread on all consumer methods')

        self._dmcs_consumer = Consumer(self._base_broker_url, self.PP_FOREMAN_CONSUME, self._base_msg_format)
        try:
            _thread.start_new_thread( self.run_dmcs_consumer, ("thread-dmcs-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start DMCS consumer thread, exiting...')
            sys.exit(99)

        self._forwarder_consumer = Consumer(self._base_broker_url, self.FORWARDER_PUBLISH, self._base_msg_format)
        try:
            _thread.start_new_thread( self.run_forwarder_consumer, ("thread-forwarder-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start FORWARDERS consumer thread, exiting...')
            sys.exit(100)

        self._ncsa_consumer = Consumer(self._ncsa_broker_url, self.NCSA_PUBLISH, self._base_msg_format)
        try:
            _thread.start_new_thread( self.run_ncsa_consumer, ("thread-ncsa-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start NCSA consumer thread, exiting...')
            sys.exit(101)

        self._ack_consumer = Consumer(self._base_broker_url, self.PP_FOREMAN_ACK_PUBLISH, self._base_msg_format)
        try:
            _thread.start_new_thread( self.run_ack_consumer, ("thread-ack-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start ACK consumer thread, exiting...')
            sys.exit(102)

        LOGGER.info('Finished starting all three consumer threads')


    def run_dmcs_consumer(self, threadname, delay):
        self._dmcs_consumer.run(self.on_dmcs_message)


    def run_forwarder_consumer(self, threadname, delay):
        self._forwarder_consumer.run(self.on_forwarder_message)


    def run_ncsa_consumer(self, threadname, delay):
        self._ncsa_consumer.run(self.on_ncsa_message)

    def run_ack_consumer(self, threadname, delay):
        self._ack_consumer.run(self.on_ack_message)



    def setup_publishers(self):
        LOGGER.info('Setting up Base publisher on %s using %s', self._base_broker_url, self._base_msg_format)
        LOGGER.info('Setting up NCSA publisher on %s using %s', self._ncsa_broker_url, self._ncsa_msg_format)
        self._base_publisher = SimplePublisher(self._pub_base_broker_url, self._base_msg_format)
        self._ncsa_publisher = SimplePublisher(self._pub_ncsa_broker_url, self._ncsa_msg_format)



    def on_dmcs_message(self, ch, method, properties, body):
        #msg_dict = yaml.load(body) 
        msg_dict = body 
        LOGGER.info('In DMCS message callback')
        LOGGER.debug('Thread in DMCS callback is %s', _thread.get_ident())
        LOGGER.info('Message from DMCS callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def on_forwarder_message(self, ch, method, properties, body):
        LOGGER.info('In Forwarder message callback, thread is %s', _thread.get_ident())
        LOGGER.info('forwarder callback msg body is: %s', str(body))
        pass

    def on_ncsa_message(self,ch, method, properties, body):
        LOGGER.info('In ncsa message callback, thread is %s', _thread.get_ident())
        #msg_dict = yaml.load(body)
        msg_dict = body
        LOGGER.info('ncsa msg callback body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def on_ack_message(self, ch, method, properties, body):
        msg_dict = body 
        LOGGER.info('In ACK message callback')
        LOGGER.debug('Thread in ACK callback is %s', _thread.get_ident())
        LOGGER.info('Message from ACK callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def set_session(self, params):
        self.JOB_SCBD.set_session(params['SESSION_ID'])
        ack_id = params['ACK_ID']
        msg = {}
        msg['MSG_TYPE'] = 'NEW_SESSION_ACK'
        msg['COMPONENT_NAME'] = 'AR_FOREMAN'
        msg['ACK_ID'] = ack_id
        msg['ACK_BOOL'] = True
        route_key = params['RESPONSE_QUEUE']
        self._base_publisher.publish_message(route_key, msg)

 
    def set_visit(self, params):
        bore_sight = params['BORE_SIGHT']
        visit_id = params['VISIT_ID'] 
        self.JOB_SCBD.set_visit_id(visit_id, bore_sight)
        ack_id = params['ACK_ID']
        msg = {}

        ncsa_result = self.send_visit_boresight_to_ncsa(visit_id, bore_sight)

        msg['MSG_TYPE'] = 'PP_NEXT_VISIT_ACK'
        msg['COMPONENT_NAME'] = 'PP_FOREMAN'
        msg['ACK_ID'] = ack_id
        msg['ACK_BOOL'] = True
        route_key = params['RESPONSE_QUEUE']
        self._base_publisher.publish_message(route_key, msg)


    def send_visit_boresight_to_ncsa(self, visit_id, bore_sight):
        msg = {}
        msg['MSG_TYPE'] = 'NEXT_VISIT'
        msg['VISIT_ID'] = visit_id
        msg['BORE_SIGHT'] = bore_sight
        msg['SESSION_ID'] = self.JOB_SCBD.get_current_session()
        ack_id = self.get_next_timed_ack_id('NCSA_NEXT_VISIT_ACK')
        msg['ACK_ID'] = ack_id
        msg['RESPONSE_QUEUE'] = self.PP_FOREMAN_ACK_PUBLISH
        self._ncsa_publisher.publish_message(self.NCSA_CONSUME, msg)

        wait_time = 4
        acks = []
        acks.append(ack_id)
        self.set_pending_nonblock_acks(acks, wait_time)


    def process_start_integration(self, input_params):
        """
        Add job to Job Scoreboard
        Check forwarder health
        Check Policy, bail if necessary
        Mark Forwarder scoreboard as a result of above
        Divide work and assemble as a forwarder dictionary for NCSA
        Send work division to NCSA
        Check Policy, bail if necessary
        Persist pairings to Job Scoreboard
        Send params to Forwarders
        Confirm Forwarder Acks
        Send confirm to DMCS
        """

        ccd_list = input_params['CCD_LIST']
        job_num = str(input_params[JOB_NUM])
        visit_id = input_params['VISIT_ID']
        image_id = input_params['IMAGE_ID']
        self.JOB_SCBD.add_job(job_num, image_id, visit_id, ccd_list)

        needed_workers = len(ccd_list) / self._policy_max_ccds_per_fwdr
        if (len(ccd_list) % self._policy_max_ccds_per_fwdr) != 0:
            needed_workers = needed_workers + 1

        unknown_status = {"STATUS": "UNKNOWN", "STATE":"UNRESPONSIVE"}
        self.FWD_SCBD.setall_forwarder_params(unknown_status)

        ack_id = self.forwarder_health_check(input_params)
         
        self.ack_timer(2.5) 
        healthy_forwarders = self.ACK_SCBD.get_components_for_timed_ack(ack_id)


        num_healthy_forwarders = len(healthy_forwarders)
        # Check policy here...assign an optimal number of ccds to long haul forwarders
        if needed_workers > num_healthy_forwarders:
            idle_status = {"STATUS": "HEALTHY", "STATE":"IDLE"}
            self.FWD_SCBD.set_forwarder_params(healthy_forwarders, idle_status)
            result = self.insufficient_base_resources(input_params, healthy_forwarders)
            return result
        else:
            needed_forwarders = []
            for i in range(0, needed_workers - 1):
                needed_forwarders.append(healthy_forwarders[i])
            ready_status = {"STATUS": "HEALTHY", "STATE":"READY_WITHOUT_PARAMS"}
            self.FWD_SCBD.set_forwarder_params(needed_forwarders, ready_status)

            extra_forwarders = []
            for i in range(needed_workers, -1):
                extra_forwarders.append(healthy_forwarders[i])
            if len(extra_forwarders) != (0):
                idle_status = {"STATUS": "HEALTHY", "STATE":"IDLE"}
                self.FWD_SCBD.set_forwarder_params(extra_forwarders, idle_status)

            # Why not send all healthy forwarders to work? Because Long Haul Transfer 
            # wants 9 - 10 ccds/fwdr optimum
            work_schedule = self.divide_work(healthy_forwarders, ccd_list) 

            ack_id = self.ncsa_resources_query(input_params, work_schedule)

            self.ack_timer(5)

            #Check ACK scoreboard for response from NCSA
            ncsa_response = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
            if ncsa_response:
                pairs = {}
                ack_bool = ncsa_response['NCSA_FOREMAN']['ACK_BOOL']
                try:
                    if ack_bool == True:
                        pairs = ncsa_response['NCSA_FOREMAN']['PAIRS'] 
                except KeyError, e:
                    LOGGER.critical('PAIRS key not found in NCSA Ack msg')
                    sys.exit 200 

                # Distribute job params and tell DMCS we are ready.
                if ack_bool == True:
                    fwd_ack_id = self.distribute_job_params(input_params, pairs)
                    self.ack_timer(3)

                    fwdr_params_response = self.ACK_SCBD.get_components_for_timed_ack(fwd_ack_id)
                    if fwdr_params_response and (len(fwdr_params_response) == len(list(pairs.keys()))):
                        self.JOB_SCBD.set_value_for_job(job_num, "STATE", "FWDR_PARAMS_RECEIVED")
                        in_ready_state = {'STATE':'READY_WITH_PARAMS'}
                        self.FWD_SCBD.set_forwarder_params(fwders, in_ready_state) 
                        # Tell DMCS we are ready
                        result = self.accept_job(job_num)
                else:
                    #not enough ncsa resources to do job - Notify DMCS
                    idle_param = {'STATE': 'IDLE'}
                    self.FWD_SCBD.set_forwarder_params(healthy_forwarders, idle_param)
                    result = self.insufficient_ncsa_resources(ncsa_response)
                    return result

            else:
                result = self.ncsa_no_response(input_params)
                idle_param = {'STATE': 'IDLE'}
                self.FWD_SCBD.set_forwarder_params(list(forwarder_candidate_dict.keys()), idle_params)
                return result
                    

 
    def forwarder_health_check(self, params):
        # get timed_ack_id
        timed_ack = self.get_next_timed_ack_id("FORWARDER_HEALTH_CHECK_ACK")

        forwarders = self.FWD_SCBD.return_forwarders_list()
        job_num = params[JOB_NUM] 
        # send health check messages
        msg_params = {}
        msg_params[MSG_TYPE] = FORWARDER_HEALTH_CHECK
        msg_params['ACK_ID'] = timed_ack
        msg_params['RESPONSE_QUEUE'] = self.PP_FOREMAN_ACK_PUBLISH
        msg_params[JOB_NUM] = job_num
       
        self.JOB_SCBD.set_value_for_job(job_num, "STATE", "HEALTH_CHECK")
        for forwarder in forwarders:
            self._base_publisher.publish_message(self.FWD_SCBD.get_value_for_forwarder(forwarder,"CONSUME_QUEUE"),
                                            msg_params)

        return timed_ack


    def insufficient_base_resources(self, params, healthy_forwarders):
        # send response msg to dmcs refusing job
        job_num = str(params[JOB_NUM])
        raft_list = params[RAFTS]
        ack_id = params['ACK_ID']
        needed_workers = len(raft_list)
        LOGGER.info('Reporting to DMCS that there are insufficient healthy forwarders for job #%s', job_num)
        dmcs_params = {}
        fail_dict = {}
        dmcs_params[MSG_TYPE] = NEW_JOB_ACK
        dmcs_params[JOB_NUM] = job_num
        dmcs_params[ACK_BOOL] = False
        dmcs_params[ACK_ID] = ack_id

        ### NOTE FOR DMCS ACK PROCESSING:
        ### if ACK_BOOL == True, there will NOT be a FAIL_DETAILS section
        ### If ACK_BOOL == False, there will always be a FAIL_DICT to examine AND there will always be a 
        ###   BASE_RESOURCES inside the FAIL_DICT
        ### If ACK_BOOL == False, and the BASE_RESOURCES inside FAIL_DETAILS == 0,
        ###   there will be only NEEDED and AVAILABLE Forwarder params - nothing more
        ### If ACK_BOOL == False and BASE_RESOURCES inside FAIL_DETAILS == 1, there will always be a 
        ###   NCSA_RESOURCES inside FAIL_DETAILS set to either 0 or 'NO_RESPONSE'
        ### if NCSA_RESPONSE == 0, there will be NEEDED and AVAILABLE Distributor params
        ### if NCSA_RESOURCES == 'NO_RESPONSE' there will be nothing else 
        fail_dict['BASE_RESOURCES'] = '0'
        fail_dict[NEEDED_FORWARDERS] = str(needed_workers)
        fail_dict[AVAILABLE_FORWARDERS] = str(len(healthy_forwarders))
        dmcs_params['FAIL_DETAILS'] = fail_dict
        self._base_publisher.publish_message("dmcs_consume", dmcs_params)
        # mark job refused, and leave Forwarders in Idle state
        self.JOB_SCBD.set_value_for_job(job_num, "STATE", "JOB_ABORTED")
        self.JOB_SCBD.set_value_for_job(job_num, "TIME_JOB_ABORTED_BASE_RESOURCES", get_timestamp())
        idle_state = {"STATE": "IDLE"}
        self.FWD_SCBD.set_forwarder_params(healthy_forwarders, idle_state)
        return False


    def divide_work(self, fwdrs_list, ccd_list):
        num_fwdrs = len(fwdrs_list)
        num_ccds = len(ccd_list)
        fwdrs_keys_list = fwdrs_list.keys()
        ## XXX FIX if num_ccds == none or 1:
        ##    Throw exception

        schedule = {}
        if num_fwdrs == 1:
            schedule[fwdrs_list[0]] = ccd_list
            return schedule

        if num_ccds <= num_fwdrs:
            for k in range (0, num_ccds):
                schedule[fwdrs_list[k]] = ccd_list[k]
        else:
            ccds_per_fwdr = len(ccd_list) / num_fwdrs 
            remainder_ccds = len(ccd_list) % num_fwdrs
            offset = 0
            for i in range(0, num_fwdrs):
                tmp_list = []
                for j in range (offset, (ccds_per_fwdr + offset)):
                    if (j) >= num_ccds:
                        break
                    tmp_list.append(ccd_list[j])
                offset = offset + ccds_per_fwdr
                if remainder_ccds != 0 and i == 0:
                    for k in range(offset, offset + remainder_ccds):
                        tmp_list.append(ccd_list[k])
                    offset = offset + remainder_ccds
                #CCD_LIST = tmp_list
                schedule[fwdrs_keys_list[i]] = {} 
                schedule[fwdrs_keys_list[i]]['CCD_LIST'] = tmp_list
        return schedule


    def ncsa_resources_query(self, params, work_schedule):
        job_num = str(params[JOB_NUM])
        timed_ack_id = self.get_next_timed_ack_id("NCSA_Start_Int_Ack") 
        ncsa_params = {}
        ncsa_params[MSG_TYPE] = "NCSA_START_INTEGRATION"
        ncsa_params[JOB_NUM] = job_num
        ncsa_params['VISIT_ID'] = params['VISIT_ID']
        ncsa_params['IMAGE_ID'] = params['IMAGE_ID']
        ncsa_params['SESSION_ID'] = params['SESSION_ID']
        ncsa_params['RESPONSE_QUEUE'] = self.PP_FOREMAN_ACK_PUBLISH
        ncsa_params[ACK_ID] = timed_ack_id
        ncsa_params["FORWARDERS"] = work_schedule
        self.JOB_SCBD.set_value_for_job(job_num, "STATE", "NCSA_START_INT_SENT")
        self._ncsa_publisher.publish_message(self.NCSA_CONSUME, ncsa_params) 
        LOGGER.info('The following forwarders schedule has been sent to NCSA for pairing:')
        LOGGER.info(work_schedule)
        return timed_ack_id


    def distribute_job_params(self, params, pairs):
        #ncsa has enough resources...
        job_num = str(params[JOB_NUM])
        self.JOB_SCBD.set_pairs_for_job(job_num, pairs)          
        LOGGER.info('The following pairs will be used for Job #%s: %s',
                     job_num, pairs)
        fwd_ack_id = self.get_next_timed_ack_id("FWD_PARAMS_ACK")
        fwders = list(pairs.keys())
        fwd_params = {}
        fwd_params[MSG_TYPE] = "FORWARDER_JOB_PARAMS"
        fwd_params[JOB_NUM] = job_num
        fwd_params['IMAGE_ID'] = params['IMAGE_ID']
        fwd_params['VISIT_ID'] = params['VISIT_ID']
        fwd_params[ACK_ID] = fwd_ack_id
        for fwder in fwders:
            fwd_params["TRANSFER_PARAMS"] = pairs[fwder]
            route_key = self.FWD_SCBD.get_value_for_forwarder(fwder, "CONSUME_QUEUE")
            self._base_publisher.publish_message(route_key, fwd_params)

        return fwd_ack_id


    def accept_job(self, job_num):
        dmcs_message = {}
        dmcs_message[JOB_NUM] = job_num
        dmcs_message[MSG_TYPE] = PP_START_INTEGRATION_ACK
        dmcs_message[ACK_BOOL] = True
        self.JOB_SCBD.set_value_for_job(job_num, STATE, "JOB_ACCEPTED")
        self.JOB_SCBD.set_value_for_job(job_num, "TIME_JOB_ACCEPTED", get_timestamp())
        self._base_publisher.publish_message("dmcs_consume", dmcs_message)
        return True


    def insufficient_ncsa_resources(self, ncsa_response):
        dmcs_params = {}
        dmcs_params[MSG_TYPE] = PP_START_INTEGRATION_ACK
        dmcs_params[JOB_NUM] = job_num 
        dmcs_params[ACK_BOOL] = False
        dmcs_params[BASE_RESOURCES] = '1'
        dmcs_params[NCSA_RESOURCES] = '0'
        dmcs_params[NEEDED_DISTRIBUTORS] = ncsa_response[NEEDED_DISTRIBUTORS]
        dmcs_params[AVAILABLE_DISTRIBUTORS] = ncsa_response[AVAILABLE_DISTRIBUTORS]
        #try: FIXME - catch exception
        self._base_publisher.publish_message("dmcs_consume", dmcs_params )
        #except L1MessageError e:
        #    return False

        return True



    def ncsa_no_response(self,params):
        #No answer from NCSA...
        job_num = str(params[JOB_NUM])
        ccd_list = params['CCD_LIST']
        needed_workers = len(ccd_list)
        dmcs_params = {}
        dmcs_params[MSG_TYPE] = PP_START_INTEGRATION_ACK
        dmcs_params[JOB_NUM] = job_num 
        dmcs_params[ACK_BOOL] = False
        dmcs_params[BASE_RESOURCES] = '1'
        dmcs_params[NCSA_RESOURCES] = 'NO_RESPONSE'
        self._base_publisher.publish_message("dmcs_consume", dmcs_params )



    def process_dmcs_readout(self, params):
        job_number = params[JOB_NUM]
        pairs = self.JOB_SCBD.get_pairs_for_job(job_number)
        date - get_timestamp()
        self.JOB_SCBD.set_value_for_job(job_number, TIME_START_READOUT, date) 
        # The following line extracts the distributor FQNs from pairs dict using 
        # list comprehension values; faster than for loops
        distributors = [v['FQN'] for v in list(pairs.values())]
        forwarders = list(pairs.keys())

        ack_id = self.get_next_timed_ack_id('NCSA_READOUT')
### Send READOUT to NCSA with ACK_ID
        ncsa_params = {}
        ncsa_params[MSG_TYPE] = 'NCSA_READOUT'
        ncsa_params[ACK_ID] = ack_id
        self._ncsa_publisher.publish_message(NCSA_CONSUME, yaml.dump(ncsa_params))


        self.ack_timer(4)

        ncsa_response = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
        if ncsa_response:
            if ncsa_response['ACK_BOOL'] == True:
                #inform forwarders
                fwd_ack_id = self.get_next_timed_ack_id('FORWARDER_READOUT')
                for forwarder in forwarders:
                    name = self.FWD_SCBD.get_value_for_forwarder(forwarder, NAME)
                    routing_key = self.FWD_SCBD.get_routing_key(forwarder)
                    msg_params = {}
                    msg_params[MSG_TYPE] = 'FORWARDER_READOUT'
                    msg_params[JOB_NUM] = job_number
                    msg_params['ACK_ID'] = fwd_ack_id
                    self.FWD_SCBD.set_forwarder_state(forwarder, START_READOUT)
                    self._publisher.publish_message(routing_key, yaml.dump(msg_params))
                self.ack_timer(4)
                forwarder_responses = self.ACK_SCBD.get_components_for_timed_ack(fwd_ack_id)
                if len(forwarder_responses) == len(forwarders):
                    dmcs_params = {}
                    dmcs_params[MSG_TYPE] = 'READOUT_ACK' 
                    dmcs_params[JOB_NUM] = job_number
                    dmcs_params['ACK_BOOL'] = True
                    dmcs_params['COMMENT'] = "Readout begun at %s" % get_timestamp()
                    self._publisher.publish_message('dmcs_consume', yaml.dump(dmcs_params))
                    
            else:
                #send problem with ncsa to DMCS
                dmcs_params = {}
                dmcs_params[MSG_TYPE] = 'READOUT_ACK' 
                dmcs_params[JOB_NUM] = job_number
                dmcs_params['ACK_BOOL'] = False
                dmcs_params['COMMENT'] = 'Readout Failed: Problem at NCSA - Expected Distributor Acks is %s, Number of Distributor Acks received is %s' % (ncsa_response['EXPECTED_DISTRIBUTOR_ACKS'], ncsa_response['RECEIVED_DISTRIBUTOR_ACKS'])
                self._base_publisher.publish_message('dmcs_consume', yaml.dump(dmcs_params))
                    
        else:
            #send 'no response from ncsa' to DMCS               )
            dmcs_params = {}
            dmcs_params[MSG_TYPE] = 'READOUT_ACK' 
            dmcs_params[JOB_NUM] = job_number
            dmcs_params['ACK_BOOL'] = False
            dmcs_params['COMMENT'] = "Readout Failed: No Response from NCSA"
            self._base_publisher.publish_message('dmcs_consume', yaml.dump(dmcs_params))
                    
        

    def process_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)
        

    def get_next_timed_ack_id(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        return (ack_type + "_" + str(self._next_timed_ack_id).zfill(6))


    def ack_timer(self, seconds):
        sleep(seconds)
        return True


    def set_pending_nonblock_acks(self, acks, wait_time):
        start_time = datetime.datetime.now().time()
        expiry_time = self.add_seconds(start_time, wait_time)
        ack_msg = {}
        ack_msg[MSG_TYPE] = 'PENDING_ACK'
        ack_msg['EXPIRY_TIME'] = expiry_time
        for ack in acks:
            ack_msg[ACK_ID] = ack
            self._base_publisher.publish_message(self.PP_FOREMAN_ACK_PUBLISH, ack_msg)


    def process_pending_ack(self, params):
        self.ACK_SCBD.add_pending_nonblock_ack(params)


    def add_seconds(self, intime, secs):
        basetime = datetime.datetime(100, 1, 1, intime.hour, intime.minute, intime.second)
        newtime = basetime + datetime.timedelta(seconds=secs)
        return newtime.time()



    def extract_config_values(self, cdm):
        try:
            self._sub_name = cdm[ROOT][PFM_BROKER_NAME]      # Message broker user & passwd
            self._sub_passwd = cdm[ROOT][PFM_BROKER_PASSWD]
            self._pub_name = cdm[ROOT]['PFM_BROKER_PUB_NAME']      # Message broker user & passwd
            self._pub_passwd = cdm[ROOT]['PFM_BROKER_PUB_PASSWD']
            self._sub_ncsa_name = cdm[ROOT]['PFM_NCSA_BROKER_NAME']
            self._sub_ncsa_passwd = cdm[ROOT]['PFM_NCSA_BROKER_PASSWD']
            self._pub_ncsa_name = cdm[ROOT]['PFM_NCSA_BROKER_PUB_NAME']
            self._pub_ncsa_passwd = cdm[ROOT]['PFM_NCSA_BROKER_PUB_PASSWD']
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self._ncsa_broker_addr = cdm[ROOT][NCSA_BROKER_ADDR]
            self.forwarder_dict = cdm[ROOT][XFER_COMPONENTS]['PP_FORWARDERS']
            self._scbd_dict = cdm[ROOT]['SCOREBOARDS']
            x = cdm['BLARG']
            self._policy_max_ccds_per_fwdr = int(cdm[ROOT]['POLICY']['MAX_CCDS_PER_FWDR'])
        except KeyError as e:
            LOGGER.critical("CDM Dictionary Key error")
            LOGGER.critical("Offending Key is %s", str(e)) 
            LOGGER.critical("Bailing out...")
            sys.exit(99)



    def purge_broker(self, queues):
        for q in queues:
            cmd = "rabbitmqctl -p /tester purge_queue " + q
            os.system(cmd)


def main():
    logging.basicConfig(filename='logs/PromptProcess.log', level=logging.INFO, format=LOG_FORMAT)
    b_fm = PromptProcessDevice()
    print("Beginning BaseForeman event loop...")
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print("")
    print("Base Foreman Done.")



if __name__ == "__main__": main()
