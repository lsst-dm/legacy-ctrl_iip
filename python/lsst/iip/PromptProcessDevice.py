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
import threading
from const import *
from Scoreboard import Scoreboard
from ForwarderScoreboard import ForwarderScoreboard
from JobScoreboard import JobScoreboard
from AckScoreboard import AckScoreboard
from Consumer import Consumer
from ThreadManager import ThreadManager
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
    PP_START_INTEGRATION_ACK = "PP_START_INTEGRATION_ACK"
    NCSA_PUBLISH = "ncsa_publish"
    NCSA_CONSUME = "ncsa_consume"
    FORWARDER_PUBLISH = "forwarder_publish"
    prp = toolsmod.prp


    def __init__(self, filename=None):
        toolsmod.singleton(self)

        self._config_file = CFG_FILE
        if filename != None:
            self._config_file = filename

        LOGGER.info('Extracting values from Config dictionary')
        self.extract_config_values()


        #self.purge_broker(cdm['ROOT']['QUEUE_PURGES'])


        self._msg_actions = { 'PP_NEW_SESSION': self.set_session,
                              'PP_NEXT_VISIT': self.set_visit, 
                              'PP_START_INTEGRATION': self.process_start_integration,
                              'PP_READOUT': self.process_dmcs_readout,
                              'NCSA_RESOURCE_QUERY_ACK': self.process_ack,
                              'NCSA_START_INTEGRATION_ACK': self.process_ack,
                              'NCSA_READOUT_ACK': self.process_ack,
                              'PP_FWDR_HEALTH_CHECK_ACK': self.process_ack,
                              'PP_FWDR_XFER_PARAMS_ACK': self.process_ack,
                              'PP_FWDR_READOUT_ACK': self.process_ack,
                              'PENDING_ACK': self.process_pending_ack,
                              'NCSA_NEXT_VISIT_ACK': self.process_ack }



        self._next_timed_ack_id = 0

        self.setup_publishers()

        self.setup_scoreboards()

        LOGGER.info('pp foreman consumer setup')
        self.thread_manager = None
        self.setup_consumer_threads()

        LOGGER.info('Prompt Process Foreman Init complete')


    def setup_publishers(self):
        self._pub_base_broker_url = "amqp://" + self._pub_name + ":" + \
                                                self._pub_passwd + "@" + \
                                                str(self._base_broker_addr)

        self._pub_ncsa_broker_url = "amqp://" + self._pub_ncsa_name + ":" + \
                                                self._pub_ncsa_passwd + "@" + \
                                                str(self._ncsa_broker_addr)

        LOGGER.info('Setting up Base publisher on %s using %s', self._pub_base_broker_url, self._base_msg_format)
        self._base_publisher = SimplePublisher(self._pub_base_broker_url, self._base_msg_format)

        LOGGER.info('Setting up NCSA publisher on %s using %s', self._pub_ncsa_broker_url, self._ncsa_msg_format)
        self._ncsa_publisher = SimplePublisher(self._pub_ncsa_broker_url, self._ncsa_msg_format)


    def on_dmcs_message(self, ch, method, properties, body):
        #msg_dict = yaml.load(body) 
        msg_dict = body 
        LOGGER.info('In DMCS message callback')
        LOGGER.info('Message from DMCS callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def on_forwarder_message(self, ch, method, properties, body):
        LOGGER.info('In Forwarder message callback, thread is %s', _thread.get_ident())
        LOGGER.info('forwarder callback msg body is: %s', str(body))
        pass

    def on_ncsa_message(self,ch, method, properties, body):
        msg_dict = body
        LOGGER.info('ncsa msg callback body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def on_ack_message(self, ch, method, properties, body):
        msg_dict = body 
        LOGGER.info('In ACK message callback')
        LOGGER.info('Message from ACK callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def set_session(self, params):
        self.JOB_SCBD.set_session(params['SESSION_ID'])
        ack_id = params['ACK_ID']
        msg = {}
        msg['MSG_TYPE'] = 'PP_NEW_SESSION_ACK'
        msg['COMPONENT'] = self.COMPONENT_NAME
        msg['ACK_ID'] = ack_id
        msg['ACK_BOOL'] = True
        route_key = params['REPLY_QUEUE']
        self._base_publisher.publish_message(route_key, msg)

 
    def set_visit(self, params):
        bore_sight = params['BORE_SIGHT']
        visit_id = params['VISIT_ID'] 
        self.JOB_SCBD.set_visit_id(visit_id, bore_sight)
        ack_id = params['ACK_ID']
        msg = {}

        ncsa_result = self.send_visit_boresight_to_ncsa(visit_id, bore_sight)

        msg['MSG_TYPE'] = 'PP_NEXT_VISIT_ACK'
        msg['COMPONENT'] = self.COMPONENT_NAME
        msg['ACK_ID'] = ack_id
        msg['ACK_BOOL'] = True
        route_key = params['REPLY_QUEUE']
        self._base_publisher.publish_message(route_key, msg)


    def send_visit_boresight_to_ncsa(self, visit_id, bore_sight):
        msg = {}
        msg['MSG_TYPE'] = 'NCSA_NEXT_VISIT'
        msg['VISIT_ID'] = visit_id
        msg['BORE_SIGHT'] = bore_sight
        msg['SESSION_ID'] = self.JOB_SCBD.get_current_session()
        ack_id = self.get_next_timed_ack_id('NCSA_NEXT_VISIT_ACK')
        msg['ACK_ID'] = ack_id
        msg['REPLY_QUEUE'] = self.PP_FOREMAN_ACK_PUBLISH
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

        unknown_status = {"STATUS": "UNKNOWN", "STATE":"UNRESPONSIVE"}
        self.FWD_SCBD.setall_forwarder_params(unknown_status)

        print("Sending Forwarder Health Checks")
        ack_id = self.forwarder_health_check(input_params)
         
        self.ack_timer(2.5) 
        healthy_forwarders = self.ACK_SCBD.get_components_for_timed_ack(ack_id)

        if healthy_forwarders == None:
            self.JOB_SCBD.set_job_state(job_number, 'SCRUBBED')
            self.JOB_SCBD.set_job_status(job_number, 'INACTIVE')
            print("Telling DMCS Insufficient Forwarders for job")
            result = self.insufficient_base_resources(input_params, None)
            return result
            
        healthy_forwarders_list = list(healthy_forwarders.keys())
        print("Health check finished - %s Forwarders responded as healthy" % len(healthy_forwarders_list))
        self.prp.pprint(healthy_forwarders_list)
        print("------------------------------\n\n")
        for forwarder in healthy_forwarders_list:
            self.FWD_SCBD.set_forwarder_state(forwarder, 'BUSY')
            self.FWD_SCBD.set_forwarder_status(forwarder, 'HEALTHY')

        num_healthy_forwarders = len(healthy_forwarders_list)


        ready_status = {"STATUS": "HEALTHY", "STATE":"READY_WITHOUT_PARAMS"}
        self.FWD_SCBD.set_forwarder_params(healthy_forwarders_list, ready_status)

        work_schedule = self.divide_work(healthy_forwarders_list, ccd_list) 

        ack_id = self.ncsa_resources_query(input_params, work_schedule)

        ncsa_response = self.progressive_ack_timer(ack_id, 1, 2.0)

        #Check ACK scoreboard for response from NCSA
        if ncsa_response:
            pairs = []
            pairs = ncsa_response['NCSA_FOREMAN']['PAIRS'] 

            # Distribute job params and tell DMCS we are ready.
            fwd_ack_id = self.distribute_job_params(input_params, pairs)
            num_fwdrs = len(pairs)
            fwdr_params_response = self.progressive_ack_timer(fwd_ack_id, num_fwdrs, 3.0)

            if fwdr_params_response:
                self.JOB_SCBD.set_value_for_job(job_num, "STATE", "FWDR_PARAMS_RECEIVED")
                in_ready_state = {'STATE':'READY_WITH_PARAMS'}
                self.FWD_SCBD.set_forwarder_params(healthy_forwarders_list, in_ready_state) 
                # Tell DMCS we are ready
                result = self.accept_job(input_params['ACK_ID'],job_num)
            else:
                print("NOT GETTING A DING DANG XFER PARAMS ACK!!!")

        else:
            result = self.ncsa_no_response(input_params)
            idle_params = {'STATE': 'IDLE'}
            self.FWD_SCBD.set_forwarder_params(needed_forwarders, idle_params)
            return result
                    

 
    def forwarder_health_check(self, params):
        # get timed_ack_id
        timed_ack = self.get_next_timed_ack_id("PP_FWDR_HEALTH_CHECK_ACK")

        forwarders = self.FWD_SCBD.return_forwarders_list()
        job_num = params[JOB_NUM] 
        # send health check messages
        msg_params = {}
        msg_params[MSG_TYPE] = 'PP_FWDR_HEALTH_CHECK'
        msg_params['ACK_ID'] = timed_ack
        msg_params['REPLY_QUEUE'] = self.PP_FOREMAN_ACK_PUBLISH
        msg_params[JOB_NUM] = job_num
       
        self.JOB_SCBD.set_value_for_job(job_num, "STATE", "HEALTH_CHECK")
        for forwarder in forwarders:
            self._base_publisher.publish_message(self.FWD_SCBD.get_routing_key(forwarder), msg_params)

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
        dmcs_params['COMPONENT'] = self.COMPONENT_NAME
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
        self._base_publisher.publish_message("dmcs_ack_consume", dmcs_params)
        # mark job refused, and leave Forwarders in Idle state
        self.JOB_SCBD.set_value_for_job(job_num, "STATE", "JOB_ABORTED")
        self.JOB_SCBD.set_value_for_job(job_num, "TIME_JOB_ABORTED_BASE_RESOURCES", get_timestamp())
        idle_state = {"STATE": "IDLE"}
        self.FWD_SCBD.set_forwarder_params(healthy_forwarders, idle_state)
        return False


    def divide_work(self, fwdrs_list, ccd_list):
        num_fwdrs = len(fwdrs_list)
        num_ccds = len(ccd_list)

        schedule = {}
        schedule['FORWARDER_LIST'] = []
        schedule['CCD_LIST'] = []  # A list of ccd lists; index of main list matches same forwarder list index
        FORWARDER_LIST = []
        CCD_LIST = [] # This is a 'list of lists'
        if num_fwdrs == 1:
            FORWARDER_LIST.append(fwdrs_list[0])
            CCD_LIST.append(ccd_list)
            schedule['FORWARDERS_LIST'] = FORWARDER_LIST
            schedule['CCD_LIST'] = CCD_LIST
            return schedule

        if num_ccds <= num_fwdrs:
            for k in range (0, num_ccds):
                little_list = []
                FORWARDER_LIST.append(fwdrs_list[k])
                little_list.append(ccd_list[k])
                CCD_LIST.append(list(little_list))  # Need a copy here...
                schedule['FORWARDER_LIST'] = FORWARDER_LIST
                schedule['CCD_LIST'] = CCD_LIST
        else:
            ccds_per_fwdr = len(ccd_list) // num_fwdrs 
            remainder_ccds = len(ccd_list) % num_fwdrs
            offset = 0
            for i in range(0, num_fwdrs):
                tmp_list = []
                for j in range (offset, (ccds_per_fwdr + offset)):
                    if (j) >= num_ccds:
                        break
                    tmp_list.append(ccd_list[j])
                #    CCD_LIST.append(ccd_list[j])
                offset = offset + ccds_per_fwdr
                if remainder_ccds != 0 and i == 0:
                    for k in range(offset, offset + remainder_ccds):
                        tmp_list.append(ccd_list[k])
                    offset = offset + remainder_ccds
                FORWARDER_LIST.append(fwdrs_list[i])
                CCD_LIST.append(list(tmp_list))
                
                #schedule[fwdrs_list[i]] = {} 
                #schedule[fwdrs_list[i]]['CCD_LIST'] = tmp_list
            schedule['FORWARDER_LIST'] = FORWARDER_LIST
            schedule['CCD_LIST'] = CCD_LIST

        return schedule


    def ncsa_resources_query(self, params, work_schedule):
        job_num = str(params[JOB_NUM])
        timed_ack_id = self.get_next_timed_ack_id("NCSA_START_INTEGRATION_ACK") 
        ncsa_params = {}
        ncsa_params[MSG_TYPE] = "NCSA_START_INTEGRATION"
        ncsa_params[JOB_NUM] = job_num
        ncsa_params['VISIT_ID'] = params['VISIT_ID']
        ncsa_params['IMAGE_ID'] = params['IMAGE_ID']
        ncsa_params['SESSION_ID'] = params['SESSION_ID']
        ncsa_params['REPLY_QUEUE'] = self.PP_FOREMAN_ACK_PUBLISH
        ncsa_params[ACK_ID] = timed_ack_id
        ncsa_params["FORWARDERS"] = work_schedule
        self.JOB_SCBD.set_value_for_job(job_num, "STATE", "NCSA_START_INT_SENT")
        self._ncsa_publisher.publish_message(self.NCSA_CONSUME, ncsa_params) 
        LOGGER.info('The following forwarders schedule has been sent to NCSA for pairing:')
        LOGGER.info(work_schedule)
        return timed_ack_id


    def distribute_job_params(self, params, pairs):
        """ pairs param is a list of dicts. (look at messages.yaml, search for 'PAIR' key, and copy here
        """
        #ncsa has enough resources...
        job_num = str(params[JOB_NUM])
        self.JOB_SCBD.set_pairs_for_job(job_num, pairs)          
        LOGGER.info('The following pairs will be used for Job #%s: %s',
                     job_num, pairs)
        fwd_ack_id = self.get_next_timed_ack_id("FWD_PARAMS_ACK")
        fwd_params = {}
        fwd_params[MSG_TYPE] = "PP_FWDR_XFER_PARAMS"
        fwd_params[JOB_NUM] = job_num
        fwd_params['IMAGE_ID'] = params['IMAGE_ID']
        fwd_params['VISIT_ID'] = params['VISIT_ID']
        fwd_params['REPLY_QUEUE'] = self.PP_FOREMAN_ACK_PUBLISH
        fwd_params[ACK_ID] = fwd_ack_id
        fwd_params['XFER_PARAMS'] = {}
        for i in range(0, len(pairs)):
            ddict = {}
            ddict = pairs[i]
            fwdr = ddict['FORWARDER']
            fwd_params['XFER_PARAMS']['CCD_LIST'] = ddict['CCD_LIST']
            fwd_params['XFER_PARAMS']['DISTRIBUTOR'] = ddict['DISTRIBUTOR']
            route_key = self.FWD_SCBD.get_value_for_forwarder(fwdr, "CONSUME_QUEUE")
            self._base_publisher.publish_message(route_key, fwd_params)

        return fwd_ack_id


    def accept_job(self, ack_id, job_num):
        dmcs_message = {}
        dmcs_message[JOB_NUM] = job_num
        dmcs_message[MSG_TYPE] = self.PP_START_INTEGRATION_ACK
        dmcs_message['COMPONENT'] = self.COMPONENT_NAME
        dmcs_message[ACK_BOOL] = True
        dmcs_message['ACK_ID'] = ack_id
        self.JOB_SCBD.set_value_for_job(job_num, STATE, "JOB_ACCEPTED")
        self.JOB_SCBD.set_value_for_job(job_num, "TIME_JOB_ACCEPTED", get_timestamp())
        self._base_publisher.publish_message("dmcs_ack_consume", dmcs_message)
        return True


    def ncsa_no_response(self,params):
        #No answer from NCSA...
        job_num = str(params[JOB_NUM])
        ccd_list = params['CCD_LIST']
        needed_workers = len(ccd_list)
        dmcs_params = {}
        dmcs_params[MSG_TYPE] = self.PP_START_INTEGRATION_ACK
        dmcs_params['COMPONENT'] = self.COMPONENT_NAME
        dmcs_params[JOB_NUM] = job_num 
        dmcs_params[ACK_BOOL] = False
        dmcs_params[BASE_RESOURCES] = '1'
        dmcs_params[NCSA_RESOURCES] = 'NO_RESPONSE'
        self._base_publisher.publish_message("dmcs_ack_consume", dmcs_params )



    def process_dmcs_readout(self, params):
        job_number = params[JOB_NUM]
        pairs = self.JOB_SCBD.get_pairs_for_job(job_number)

        ### Send READOUT to NCSA with ACK_ID
        ack_id = self.get_next_timed_ack_id('NCSA_READOUT_ACK')
        ncsa_params = {}
        ncsa_params[MSG_TYPE] = 'NCSA_READOUT'
        ncsa_params['JOB_NUM'] = job_number
        ncsa_params['VISIT_ID'] = params['VISIT_ID']
        ncsa_params['SESSION_ID'] = params['SESSION_ID']
        ncsa_params['IMAGE_ID'] = params['IMAGE_ID']
        ncsa_params['REPLY_QUEUE'] = 'pp_foreman_ack_publish'
        ncsa_params[ACK_ID] = ack_id
        self._ncsa_publisher.publish_message(self.NCSA_CONSUME, ncsa_params)

        ncsa_response = self.progressive_ack_timer(ack_id, 1, 3.0)

        if ncsa_response:
            if ncsa_response['NCSA_FOREMAN']['ACK_BOOL'] == True:
                #inform forwarders
                fwd_ack_id = self.get_next_timed_ack_id('PP_FWDR_READOUT_ACK')
                len_pairs = len(pairs)
                for i in range(0, len_pairs):
                    forwarder = pairs[i]['FORWARDER']
                    routing_key = self.FWD_SCBD.get_routing_key(forwarder)
                    msg_params = {}
                    msg_params[MSG_TYPE] = 'PP_FWDR_READOUT'
                    msg_params[JOB_NUM] = job_number
                    msg_params['REPLY_QUEUE'] = 'pp_foreman_ack_publish'
                    msg_params['ACK_ID'] = fwd_ack_id
                    self.FWD_SCBD.set_forwarder_state(forwarder, 'START_READOUT')
                    self._base_publisher.publish_message(routing_key, msg_params)

                forwarder_responses = self.progressive_ack_timer(fwd_ack_id, len_pairs, 4.0)

                if forwarder_responses:
                    dmcs_params = {}
                    dmcs_params[MSG_TYPE] = 'PP_READOUT_ACK' 
                    dmcs_params[JOB_NUM] = job_number
                    dmcs_params['COMPONENT'] = self.COMPONENT_NAME
                    dmcs_params['ACK_BOOL'] = True
                    dmcs_params['ACK_ID'] = params['ACK_ID']
                    self._base_publisher.publish_message(params['REPLY_QUEUE'], dmcs_params)
                    
            else:
                #send problem with ncsa to DMCS
                dmcs_params = {}
                dmcs_params[MSG_TYPE] = 'PP_READOUT_ACK' 
                dmcs_params[JOB_NUM] = job_number
                dmcs_params['COMPONENT'] = self.COMPONENT_NAME
                dmcs_params['ACK_BOOL'] = False
                dmcs_params['ACK_ID'] = params['ACK_ID']
                self._base_publisher.publish_message('dmcs_ack_consume', dmcs_params)
                    
        else:
            #send 'no response from ncsa' to DMCS               )
            dmcs_params = {}
            dmcs_params[MSG_TYPE] = 'PP_READOUT_ACK' 
            dmcs_params[JOB_NUM] = job_number
            dmcs_params['COMPONENT'] = self.COMPONENT_NAME
            dmcs_params['ACK_BOOL'] = False
            dmcs_params['ACK_ID'] = params['ACK_ID']
            self._base_publisher.publish_message(params['REPLY_QUEUE'], dmcs_params)
                    
        

    def process_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)
        

    def get_next_timed_ack_id(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        return (ack_type + "_" + str(self._next_timed_ack_id).zfill(6))


    def ack_timer(self, seconds):
        sleep(seconds)
        return True

    def progressive_ack_timer(self, ack_id, expected_replies, seconds):
        counter = 0.0
        while (counter < seconds):
            sleep(0.5)
            response = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
            if len(list(response.keys())) == expected_replies:
                print("Received all %s Acks in %s seconds." % (expected_replies, counter)) 
                return response
            counter = counter + 0.5

        ## Try one final time 
        response = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
        if len(list(response.keys())) == expected_replies:
            return response
        else:
            return None


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



    def extract_config_values(self):
        LOGGER.info('Reading YAML Config file %s' % self._config_file)
        try:
            cdm = toolsmod.intake_yaml_file(self._config_file)
        except IOError as e:
            LOGGER.critical("Unable to find CFG Yaml file %s\n" % self._config_file)
            sys.exit(101)

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
            self._forwarder_dict = cdm[ROOT][XFER_COMPONENTS]['PP_FORWARDERS']
            self._scbd_dict = cdm[ROOT]['SCOREBOARDS']
            self._policy_max_ccds_per_fwdr = int(cdm[ROOT]['POLICY']['MAX_CCDS_PER_FWDR'])
        except KeyError as e:
            LOGGER.critical("CDM Dictionary Key error")
            LOGGER.critical("Offending Key is %s", str(e)) 
            LOGGER.critical("Bailing out...")
            print("KeyError when reading CFG file. Check logs...exiting...")
            sys.exit(99)

        self._base_msg_format = 'YAML'
        self._ncsa_msg_format = 'YAML'

        if 'BASE_MSG_FORMAT' in cdm[ROOT]:
            self._base_msg_format = cdm[ROOT][BASE_MSG_FORMAT]

        if 'NCSA_MSG_FORMAT' in cdm[ROOT]:
            self._ncsa_msg_format = cdm[ROOT][NCSA_MSG_FORMAT]

    def setup_consumer_threads(self):
        LOGGER.info('Building _base_broker_url')
        base_broker_url = "amqp://" + self._sub_name + ":" + \
                                            self._sub_passwd + "@" + \
                                            str(self._base_broker_addr)

        ncsa_broker_url = "amqp://" + self._sub_ncsa_name + ":" + \
                                            self._sub_ncsa_passwd + "@" + \
                                            str(self._ncsa_broker_addr)

        # Set up kwargs that describe consumers to be started
        # The Archive Device needs three message consumers
        kws = {}
        md = {}
        md['amqp_url'] = base_broker_url
        md['name'] = 'Thread-pp_foreman_consume'
        md['queue'] = 'pp_foreman_consume'
        md['callback'] = self.on_dmcs_message
        md['format'] = "YAML"
        md['test_val'] = None
        kws[md['name']] = md

        md = {}
        md['amqp_url'] = base_broker_url
        md['name'] = 'Thread-pp_foreman_ack_publish'
        md['queue'] = 'pp_foreman_ack_publish'
        md['callback'] = self.on_ack_message
        md['format'] = "YAML"
        md['test_val'] = 'test_it'
        kws[md['name']] = md

        md = {}
        md['amqp_url'] = ncsa_broker_url
        md['name'] = 'Thread-ncsa_publish'
        md['queue'] = 'ncsa_publish'
        md['callback'] = self.on_ncsa_message
        md['format'] = "YAML"
        md['test_val'] = 'test_it'
        kws[md['name']] = md

        self.thread_manager = ThreadManager('thread-manager', kws)
        self.thread_manager.start()


    def setup_scoreboards(self):
        # Create Redis Forwarder table with Forwarder info
        self.FWD_SCBD = ForwarderScoreboard('PP_FWD_SCBD', self._scbd_dict['PP_FWD_SCBD'], self._forwarder_dict)
        self.JOB_SCBD = JobScoreboard('PP_JOB_SCBD', self._scbd_dict['PP_JOB_SCBD'])
        self.ACK_SCBD = AckScoreboard('PP_ACK_SCBD', self._scbd_dict['PP_ACK_SCBD'])


    def purge_broker(self, queues):
        for q in queues:
            cmd = "rabbitmqctl -p /tester purge_queue " + q
            os.system(cmd)


def main():
    logging.basicConfig(filename='logs/PromptProcess.log', level=logging.DEBUG, format=LOG_FORMAT)
    b_fm = PromptProcessDevice()
    print("Beginning PromptProcessDevice event loop...")
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print("")
    print("Base Foreman Done.")



if __name__ == "__main__": main()
