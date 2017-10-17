import toolsmod
from toolsmod import get_timestamp
import logging
import pika
import redis
import yaml
import sys
import os
import copy
import pprint
import time
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


class ArchiveDevice:
    COMPONENT_NAME = 'ARCHIVE_FOREMAN'
    AR_FOREMAN_CONSUME = "ar_foreman_consume"
    ARCHIVE_CTRL_PUBLISH = "archive_ctrl_publish"
    ARCHIVE_CTRL_CONSUME = "archive_ctrl_consume"
    AR_FOREMAN_ACK_PUBLISH = "ar_foreman_ack_publish"
    START_INTEGRATION_XFER_PARAMS = {}
    prp = toolsmod.prp


    def __init__(self, filename=None):
        toolsmod.singleton(self)

        self._config_file = 'L1SystemCfg.yaml'
        if filename != None:
            self._config_file = filename

        LOGGER.info('Extracting values from Config dictionary')
        self.extract_config_values()


        #self.purge_broker(cdm['ROOT']['QUEUE_PURGES'])



        self._msg_actions = { 'AR_START_INTEGRATION': self.process_start_integration,
                              'AR_NEW_SESSION': self.set_session,
                              'AR_NEXT_VISIT': self.set_visit,
                              'AR_READOUT': self.process_dmcs_readout,
                              'AR_FWDR_HEALTH_CHECK_ACK': self.process_ack,
                              'AR_FWDR_XFER_PARAMS_ACK': self.process_ack,
                              'AR_FWDR_READOUT_ACK': self.process_ack,
                              'AR_ITEMS_XFERD_ACK': self.process_ack,
                              'NEW_ARCHIVE_ITEM_ACK': self.process_ack }


        self._next_timed_ack_id = 0

        self.setup_publishers()

        self.setup_scoreboards()

        LOGGER.info('ar foreman consumer setup')
        self.thread_manager = None
        self.setup_consumer_threads()

        LOGGER.info('Archive Foreman Init complete')


    def setup_publishers(self):
        self.pub_base_broker_url = "amqp://" + self._msg_pub_name + ":" + \
                                            self._msg_pub_passwd + "@" + \
                                            str(self._base_broker_addr)
        LOGGER.info('Setting up Base publisher on %s using %s', self.pub_base_broker_url, self._base_msg_format)
        self._publisher = SimplePublisher(self.pub_base_broker_url, self._base_msg_format)


    def on_ar_foreman_message(self, ch, method, properties, body):
        #msg_dict = yaml.load(body) 
        ch.basic_ack(method.delivery_tag)
        msg_dict = body 
        LOGGER.info('In AR Foreman message callback')
        LOGGER.info('Message from DMCS to AR Foreman callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def on_archive_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        LOGGER.info('AR CTRL callback msg body is: %s', str(body))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def on_ack_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag) 
        msg_dict = body 
        LOGGER.info('In ACK message callback')
        LOGGER.info('Message from ACK callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    


    def process_start_integration(self, params):
        # receive new job_number and image_id; session and visit are current
        # and deep copy it with some additions such as aseesion and visit
        session_id = self.get_current_session()
        visit_id = self.get_current_visit()
        job_number = params[JOB_NUM]
        image_id = params[IMAGE_ID]
        ccds = params['CCD_LIST']
        start_int_ack_id = params[ACK_ID]

        # next, run health check
        health_check_ack_id = self.get_next_timed_ack_id('AR_FWDR_HEALTH_ACK')
        num_fwdrs_checked = self.fwdr_health_check(health_check_ack_id)

        # Add job scbd entry
        self.JOB_SCBD.add_job(job_number, image_id, visit_id, ccds)
        self.JOB_SCBD.set_job_params(job_number, {'SESSION_ID': session_id, 
                                                  'VISIT_ID': visit_id})
        self.ack_timer(1.5)

        healthy_fwdrs = self.ACK_SCBD.get_components_for_timed_ack(health_check_ack_id)
        if healthy_fwdrs == None:
            self.refuse_job(params, "No forwarders available")
            self.JOB_SCBD.set_job_state(job_number, 'SCRUBBED')
            self.JOB_SCBD.set_job_status(job_number, 'INACTIVE')
            return

        for forwarder in healthy_fwdrs:
            self.FWD_SCBD.set_forwarder_state(forwarder, 'BUSY')
            self.FWD_SCBD.set_forwarder_status(forwarder, 'HEALTHY')

        # send new_archive_item msg to archive controller
        start_int_params = {}
        ac_timed_ack = self.get_next_timed_ack_id('AR_CTRL_NEW_ITEM')
        start_int_params[MSG_TYPE] = 'NEW_ARCHIVE_ITEM'
        start_int_params['ACK_ID'] = ac_timed_ack
        start_int_params['JOB_NUM'] = job_number
        start_int_params['SESSION_ID'] = session_id
        start_int_params['VISIT_ID'] = visit_id
        start_int_params['IMAGE_ID'] = image_id
        start_int_params['REPLY_QUEUE'] = self.AR_FOREMAN_ACK_PUBLISH
        self.JOB_SCBD.set_job_state(job_number, 'AR_NEW_ITEM_QUERY')
        self._publisher.publish_message(self.ARCHIVE_CTRL_CONSUME, start_int_params)

        ar_response = self.progressive_ack_timer(ac_timed_ack, 1, 2.0)

        # if ar_response == None:
        #    raise L1 exception and bail out
       
        """ 
        if ar_response['ARCHIVE_CTRL'][ACK_BOOL] == False:
            start_int_params['ACK_ID'] = start_int__ack_id
            self.refuse_job(start_int_params, ar_response['AR_CTRL']['FAIL_DETAILS'])
            scrub_params = {'STATE':'scrubbed', 'STATUS':'INACTIVE'}
            self.JOB_SCBD.set_job_params(job_number, scrub_params)
            fscbd_params = {'STATE':'IDLE', 'STATUS':'HEALTHY'}
            self.FWD_SCBD.set_forwarder_params(healthy_forwarders, fscbd_params)
            return

        else:
            start_int_params['ACK_ID'] = start_int_ack_id
            self.refuse_job(start_int_params, "No response from archive")
            scrub_params = {'STATE':'scrubbed', 'STATUS':'INACTIVE'}
            self.JOB_SCBD.set_job_params(job_number, scrub_params)
            fscbd_params = {'STATE':'IDLE', 'STATUS':'HEALTHY'}
            self.FWD_SCBD.set_forwarder_params(healthy_fwdrs, fscbd_params)
            return
        """
        target_dir = ar_response['ARCHIVE_CTRL']['TARGET_DIR']
        self.JOB_SCBD.set_job_params(job_number, {'STATE':'AR_NEW_ITEM_RESPONSE', 'TARGET_DIR': dir})
        

        # divide image fetch across forwarders
        list_of_fwdrs = list(healthy_fwdrs.keys())
        work_schedule = self.divide_work(list_of_fwdrs, ccds)

        # send image_id, target dir, and job, session,visit and work to do to healthy forwarders
        self.JOB_SCBD.set_value_for_job(job_number, 'STATE','SENDING_XFER_PARAMS')
        self.JOB_SCBD.set_work_schedule_for_job(job_number, work_schedule)
       
        xfer_params_ack_id = self.get_next_timed_ack_id("AR_FWDR_PARAMS_ACK") 

        start_int_params = {}
        minidict = {}
        minidict['IP_ADDR'] = self.archive_ip
        minidict['NAME'] = self.archive_name
        minidict['FQN'] = self.archive_fqn
        minidict['CCD_LIST'] = []
        start_int_params[MSG_TYPE] = 'AR_FWDR_XFER_PARAMS'
        start_int_params['XFER_PARAMS'] = minidict
        start_int_params['TARGET_DIR'] = target_dir
        start_int_params[ACK_ID] = xfer_params_ack_id
        start_int_params['REPLY_QUEUE'] = self.AR_FOREMAN_ACK_PUBLISH
        start_int_params[JOB_NUM] = job_number
        start_int_params['IMAGE_ID'] = image_id
        start_int_params['SESSION_ID'] = session_id
        start_int_params['VISIT_ID'] = visit_id
        self.send_xfer_params(start_int_params, work_schedule)



        # receive ack back from forwarders that they have job params
        params_acks = self.progressive_ack_timer(xfer_params_ack_id, len(list_of_fwdrs), 2.0)

        # if params_acks == None:
        #     raise L1Exception and bail

        self.JOB_SCBD.set_value_for_job(job_number,'STATE','XFER_PARAMS_SENT')

        ##################ACCEPT_JOB
        st_int_params_ack = {}
        st_int_params_ack['ACK_ID'] = start_int_ack_id
        st_int_params_ack['JOB_NUM'] = job_number
        st_int_params_ack['SESSION_ID'] = session_id
        st_int_params_ack['IMAGE_ID'] = image_id
        st_int_params_ack['VISIT_ID'] = visit_id
        st_int_params_ack['COMPONENT'] = self.COMPONENT_NAME
        self.accept_job(st_int_params_ack)
        self.JOB_SCBD.set_value_for_job(job_number, STATE, "JOB_ACCEPTED")
        fscbd_params = {'STATE':'AWAITING_READOUT'}
        self.FWD_SCBD.set_forwarder_params(healthy_fwdrs, fscbd_params)


    def fwdr_health_check(self, ack_id):
        msg_params = {}
        msg_params[MSG_TYPE] = 'AR_FWDR_HEALTH_CHECK'
        msg_params[ACK_ID] = ack_id
        msg_params[REPLY_QUEUE] = self.AR_FOREMAN_ACK_PUBLISH

        forwarders = self.FWD_SCBD.return_available_forwarders_list()
        state_status = {"STATE": "HEALTH_CHECK", "STATUS": "UNKNOWN"}
        self.FWD_SCBD.set_forwarder_params(forwarders, state_status)
        for forwarder in forwarders:
            self._publisher.publish_message(self.FWD_SCBD.get_value_for_forwarder(forwarder,"CONSUME_QUEUE"), msg_params)
        return len(forwarders)


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
            schedule['FORWARDER_LIST'] = FORWARDER_LIST
            schedule['CCD_LIST'] = CCD_LIST
            return schedule

        if num_ccds <= num_fwdrs:
            for k in range (0, num_ccds):
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
                offset = offset + ccds_per_fwdr
                if remainder_ccds != 0 and i == 0:
                    for k in range(offset, offset + remainder_ccds):
                        tmp_list.append(ccd_list[k])
                    offset = offset + remainder_ccds
                FORWARDER_LIST.append(fwdrs_list[i])
                CCD_LIST.append(list(tmp_list))
            schedule['FORWARDER_LIST'] = FORWARDER_LIST
            schedule['CCD_LIST'] = CCD_LIST

        return schedule


    def send_xfer_params(self, params, work_schedule):
        fwdrs = work_schedule['FORWARDER_LIST']
        CCD_LIST = work_schedule['CCD_LIST']
        for i in range(0, len(fwdrs)):
            params['XFER_PARAMS']['CCD_LIST'] = CCD_LIST[i] 
            route_key = self.FWD_SCBD.get_value_for_forwarder(fwdrs[i], "CONSUME_QUEUE")
            self._publisher.publish_message(route_key, params)


    def accept_job(self, params):
        dmcs_message = {}
        dmcs_message['JOB_NUM'] = params['JOB_NUM']
        dmcs_message[MSG_TYPE] = 'AR_START_INTEGRATION_ACK'
        dmcs_message['ACK_ID'] = params['ACK_ID']
        dmcs_message['SESSION_ID'] = params['SESSION_ID']
        dmcs_message['VISIT_ID'] = params['VISIT_ID']
        dmcs_message['IMAGE_ID'] = params['IMAGE_ID']
        dmcs_message[ACK_BOOL] = True
        dmcs_message['COMPONENT'] = self.COMPONENT_NAME
        self._publisher.publish_message("dmcs_ack_consume", dmcs_message)


    def refuse_job(self, params, fail_details):
        dmcs_message = {}
        dmcs_message[JOB_NUM] = params[JOB_NUM]
        dmcs_message[MSG_TYPE] = 'AR_START_INTEGRATION_ACK'
        dmcs_message['ACK_ID'] = params['ACK_ID']
        dmcs_message['SESSION_ID'] = params['SESSION_ID']
        dmcs_message['VISIT_ID'] = params['VISIT_ID']
        dmcs_message['IMAGE_ID'] = params['IMAGE_ID']
        dmcs_message[ACK_BOOL] = False 
        dmcs_message['COMPONENT'] = self.COMPONENT_NAME
        self.JOB_SCBD.set_value_for_job(params[JOB_NUM], STATE, "JOB_REFUSED")
        self._publisher.publish_message("dmcs_ack_consume", dmcs_message)


    def process_dmcs_readout(self, params):
        readout_ack_id = params[ACK_ID]
        job_number = params[JOB_NUM]
        image_id = params[IMAGE_ID]
        # send readout to forwarders
        self.JOB_SCBD.set_value_for_job(job_number, 'STATE', 'PREPARE_READOUT')
        fwdr_readout_ack = self.get_next_timed_ack_id("AR_FWDR_READOUT_ACK")
        work_schedule = self.JOB_SCBD.get_work_schedule_for_job(job_number)
        fwdrs = work_schedule['FORWARDER_LIST']

        self.send_readout(params, fwdrs, fwdr_readout_ack)
        self.JOB_SCBD.set_value_for_job(job_number, 'STATE', 'READOUT_STARTED')

        readout_responses = self.progressive_ack_timer(fwdr_readout_ack, len(fwdrs), 4.0)

        # if readout_responses == None:
        #    raise L1 exception 

        self.process_readout_responses(readout_ack_id, image_id, readout_responses)

    def process_readout_responses(self, readout_ack_id, image_id, readout_responses):
        job_number = None
        image_id = None
        confirm_ack = self.get_next_timed_ack_id('AR_ITEMS_XFERD_ACK')
        fwdrs = list(readout_responses.keys())
        CCD_LIST = []
        FILENAME_LIST = []
        CHECKSUM_LIST = []
        for fwdr in fwdrs:
            ccds = readout_responses[fwdr]['RESULT_LIST']['CCD_LIST']
            num_ccds = len(ccds)
            fnames = readout_responses[fwdr]['RESULT_LIST']['FILENAME_LIST']
            csums = readout_responses[fwdr]['RESULT_LIST']['CHECKSUM_LIST']
            for i in range(0, num_ccds):
                msg = {}
                CCD_LIST.append(ccds[i])
                FILENAME_LIST.append(fnames[i])
                CHECKSUM_LIST.append(csums[i])
        job_number = readout_responses[fwdr][JOB_NUM]
        image_id = readout_responses[fwdr]['IMAGE_ID']
        xfer_list_msg = {}
        xfer_list_msg[MSG_TYPE] = 'AR_ITEMS_XFERD'
        xfer_list_msg[ACK_ID] = confirm_ack
        xfer_list_msg['IMAGE_ID'] = image_id
        xfer_list_msg['REPLY_QUEUE'] = self.AR_FOREMAN_ACK_PUBLISH
        xfer_list_msg['RESULT_LIST'] = {}
        xfer_list_msg['RESULT_LIST']['CCD_LIST'] = CCD_LIST
        xfer_list_msg['RESULT_LIST']['FILENAME_LIST'] = FILENAME_LIST
        xfer_list_msg['RESULT_LIST']['CHECKSUM_LIST'] = CHECKSUM_LIST
        self._publisher.publish_message(self.ARCHIVE_CTRL_CONSUME, xfer_list_msg) 
           
        xfer_check_responses = self.progressive_ack_timer(confirm_ack, 1, 4.0) 

        # if xfer_check_responses == None:
        #    raise L1 exception and bail

        results = xfer_check_responses['ARCHIVE_CTRL']['RESULT_LIST']

        ack_msg = {}
        ack_msg['MSG_TYPE'] = 'AR_READOUT_ACK'
        ack_msg['JOB_NUM'] = job_number
        ack_msg['COMPONENT'] = self.COMPONENT_NAME
        ack_msg['ACK_ID'] = readout_ack_id
        ack_msg['ACK_BOOL'] = True
        ack_msg['RESULT_LIST'] = results
        self._publisher.publish_message("dmcs_ack_consume", ack_msg)

        ### FIXME Set state as complete for Job


                   
    def send_readout(self, params, fwdrs, readout_ack):
        ro_params = {}
        job_number = params['JOB_NUM']
        ro_params['MSG_TYPE'] = 'AR_FWDR_READOUT'
        ro_params['JOB_NUM'] = job_number
        ro_params['SESSION_ID'] = self.get_current_session()
        ro_params['VISIT_ID'] = self.get_current_visit()
        ro_params['IMAGE_ID'] = params['IMAGE_ID']
        ro_params['ACK_ID'] = readout_ack
        ro_params['REPLY_QUEUE'] = self.AR_FOREMAN_ACK_PUBLISH 
        for fwdr in fwdrs:
            route_key = self.FWD_SCBD.get_value_for_forwarder(fwdr, "CONSUME_QUEUE")
            self._publisher.publish_message(route_key, ro_params)




 
    def process_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)
        

    def get_next_timed_ack_id(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        return (ack_type + "_" + str(self._next_timed_ack_id).zfill(6))


    def set_session(self, params):
        self.JOB_SCBD.set_session(params['SESSION_ID'])
        ack_id = params['ACK_ID']
        msg = {}
        msg['MSG_TYPE'] = 'AR_NEW_SESSION_ACK'
        msg['COMPONENT'] = self.COMPONENT_NAME
        msg['ACK_ID'] = ack_id
        msg['ACK_BOOL'] = True
        route_key = params['REPLY_QUEUE'] 
        self._publisher.publish_message(route_key, msg)


    def get_current_session(self):
        return self.JOB_SCBD.get_current_session()


    def set_visit(self, params):
        bore_sight = params['BORE_SIGHT']
        self.JOB_SCBD.set_visit_id(params['VISIT_ID'], bore_sight)
        ack_id = params['ACK_ID']
        msg = {}
        ## XXX FIXME Do something with the bore sight in params['BORE_SIGHT']
        msg['MSG_TYPE'] = 'AR_NEXT_VISIT_ACK'
        msg['COMPONENT'] = self.COMPONENT_NAME
        msg['ACK_ID'] = ack_id
        msg['ACK_BOOL'] = True
        route_key = params['REPLY_QUEUE'] 
        self._publisher.publish_message(route_key, msg)


    def get_current_visit(self):
        return self.JOB_SCBD.get_current_visit()
        

    def ack_timer(self, seconds):
        sleep(seconds)
        return True


    def progressive_ack_timer(self, ack_id, expected_replies, seconds):
        counter = 0.0
        while (counter < seconds):
            sleep(0.5)
            response = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
            if len(list(response.keys())) == expected_replies:
                return response
            counter = counter + 0.5

        ## Try one final time
        response = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
        if len(list(response.keys())) == expected_replies:
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
            self._msg_name = cdm[ROOT][AFM_BROKER_NAME]      # Message broker user & passwd
            self._msg_passwd = cdm[ROOT][AFM_BROKER_PASSWD]   
            self._msg_pub_name = cdm[ROOT]['AFM_BROKER_PUB_NAME']      # Message broker user & passwd
            self._msg_pub_passwd = cdm[ROOT]['AFM_BROKER_PUB_PASSWD']   
            self._ncsa_name = cdm[ROOT][NCSA_BROKER_NAME]     
            self._ncsa_passwd = cdm[ROOT][NCSA_BROKER_PASSWD]   
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self._ncsa_broker_addr = cdm[ROOT][NCSA_BROKER_ADDR]
            self._forwarder_dict = cdm[ROOT][XFER_COMPONENTS]['ARCHIVE_FORWARDERS']
            self._scbd_dict = cdm[ROOT]['SCOREBOARDS']

            # Placeholder until eventually worked out by Data Backbone team
            self.archive_fqn = cdm[ROOT]['ARCHIVE']['ARCHIVE_NAME']
            self.archive_name = cdm[ROOT]['ARCHIVE']['ARCHIVE_LOGIN']
            self.archive_ip = cdm[ROOT]['ARCHIVE']['ARCHIVE_IP']
        except KeyError as e:
            print("Dictionary error")
            print("Bailing out...")
            sys.exit(99)

        self._base_msg_format = 'YAML'

        if 'BASE_MSG_FORMAT' in cdm[ROOT]:
            self._base_msg_format = cdm[ROOT]['BASE_MSG_FORMAT']


    def setup_consumer_threads(self):
        base_broker_url = "amqp://" + self._msg_name + ":" + \
                                            self._msg_passwd + "@" + \
                                            str(self._base_broker_addr)
        LOGGER.info('Building _base_broker_url. Result is %s', base_broker_url)


        # Set up kwargs that describe consumers to be started
        # The Archive Device needs three message consumers
        kws = {}
        md = {}
        md['amqp_url'] = base_broker_url
        md['name'] = 'Thread-ar_foreman_consume'
        md['queue'] = 'ar_foreman_consume'
        md['callback'] = self.on_ar_foreman_message
        md['format'] = "YAML"
        md['test_val'] = None
        kws[md['name']] = md

        md = {}
        md['amqp_url'] = base_broker_url
        md['name'] = 'Thread-ar_foreman_ack_publish'
        md['queue'] = 'ar_foreman_ack_publish'
        md['callback'] = self.on_ack_message
        md['format'] = "YAML"
        md['test_val'] = 'test_it'
        kws[md['name']] = md

        md = {}
        md['amqp_url'] = base_broker_url
        md['name'] = 'Thread-archive_ctrl_publish'
        md['queue'] = 'archive_ctrl_publish'
        md['callback'] = self.on_archive_message
        md['format'] = "YAML"
        md['test_val'] = 'test_it'
        kws[md['name']] = md

        self.thread_manager = ThreadManager('thread-manager', kws)
        self.thread_manager.start()

    def setup_scoreboards(self):
        # Create Redis Forwarder table with Forwarder info
        self.FWD_SCBD = ForwarderScoreboard('AR_FWD_SCBD', self._scbd_dict['AR_FWD_SCBD'], self._forwarder_dict)
        self.JOB_SCBD = JobScoreboard('AR_JOB_SCBD', self._scbd_dict['AR_JOB_SCBD'])
        self.ACK_SCBD = AckScoreboard('AR_ACK_SCBD', self._scbd_dict['AR_ACK_SCBD'])


    def purge_broker(self, queues):
        for q in queues:
            cmd = "rabbitmqctl -p /tester purge_queue " + q
            os.system(cmd)


def main():
    logging.basicConfig(filename='logs/BaseForeman.log', level=logging.INFO, format=LOG_FORMAT)
    a_fm = ArchiveDevice()
    print("Beginning ArchiveForeman event loop...")
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print("")
    print("Archive Device Done.")



if __name__ == "__main__": main()
