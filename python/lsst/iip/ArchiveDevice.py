import toolsmod
from toolsmod import get_timestamp
import logging
import pika
import redis
import yaml
import sys
import os
import copy
import time
from time import sleep
import thread
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


class ArchiveDevice:
    AR_JOB_SCBD = None
    AR_FWD_SCBD = None
    AR_ACK_SCBD = None
    COMPONENT_NAME = 'ARCHIVE_FOREMAN'
    AR_FOREMAN_CONSUME = "ar_foreman_consume"
    AR_CTRL_PUBLISH = "ar_ctrl_publish"
    AR_CTRL_CONSUME = "ar_ctrl_consume"
    AR_FOREMAN_ACK_PUBLISH = "ar_foreman_ack_publish"
    YAML = 'YAML'
    START_INTEGRATION_XFER_PARAMS = {}


    def __init__(self, filename=None):
        toolsmod.singleton(self)

        self._config_file = 'ForemanCfg.yaml'
        if filename != None:
            self._config_file = filename

        cdm = toolsmod.intake_yaml_file(self._config_file)

        try:
            self._base_name = cdm[ROOT][BASE_BROKER_NAME]      # Message broker user & passwd
            self._base_passwd = cdm[ROOT][BASE_BROKER_PASSWD]   
            self._ncsa_name = cdm[ROOT][NCSA_BROKER_NAME]     
            self._ncsa_passwd = cdm[ROOT][NCSA_BROKER_PASSWD]   
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self._ncsa_broker_addr = cdm[ROOT][NCSA_BROKER_ADDR]
            self._forwarder_dict = cdm[ROOT][XFER_COMPONENTS]['ARCHIVE_FORWARDERS']
            self._scbd_dict = cdm[ROOT]['SCOREBOARDS']
        except KeyError as e:
            print "Dictionary error"
            print "Bailing out..."
            sys.exit(99)

        self.START_INTEGRATION_XFER_PARAMS[MSG_TYPE] = 'AR_FWDR_XFER_PARAMS'
        try:
            self.START_INTEGRATION_XFER_PARAMS[FQN] = cdm[ROOT]['ARCHIVE_NAME']
            self.START_INTEGRATION_XFER_PARAMS[NAME] = cdm[ROOT]['ARCHIVE_LOGIN']
            self.START_INTEGRATION_XFER_PARAMS[HOSTNAME] = cdm[ROOT]['ARCHIVE_HOSTNAME']
            self.START_INTEGRATION_XFER_PARAMS[IP_ADDR] = cdm[ROOT]['ARCHIVE_IP']
        except KeyError as e:
            pass


        if 'QUEUE_PURGES' in cdm[ROOT]:
            self.purge_broker(cdm['ROOT']['QUEUE_PURGES'])

        self._base_msg_format = self.YAML

        if 'BASE_MSG_FORMAT' in cdm[ROOT]:
            self._base_msg_format = cdm[ROOT][BASE_MSG_FORMAT]


        self._base_broker_url = 'amqp_url'
        self._next_timed_ack_id = 0


        # Create Redis Forwarder table with Forwarder info
        self.FWD_SCBD = ForwarderScoreboard(self._scbd_dict['AR_FWD_SCBD'], self._forwarder_dict)
        self.JOB_SCBD = JobScoreboard(self._scbd_dict['AR_JOB_SCBD'])
        self.ACK_SCBD = AckScoreboard(self._scbd_dict['AR_ACK_SCBD'])

        self._msg_actions = { 'START_INTEGRATION': self.process_start_integration,
                              'NEW_SESSION': self.set_session,
                              'NEXT_VISIT': self.set_visit,
                              'READOUT': self.process_dmcs_readout,
                              'FORWARDER_HEALTH_ACK': self.process_ack,
                              'FORWARDER_JOB_PARAMS_ACK': self.process_ack,
                              'FORWARDER_READOUT_ACK': self.process_ack,
                              'NEW_ARCHIVE_ITEM_ACK': self.process_ack }


        self._base_broker_url = "amqp://" + self._base_name + ":" + self._base_passwd + "@" + str(self._base_broker_addr)


        LOGGER.info('Building _base_broker_url. Result is %s', self._base_broker_url)

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
        LOGGER.info('Setting up consumers on %s', self._base_broker_url)
        LOGGER.info('Running start_new_thread on all consumer methods')

        self._dmcs_consumer = Consumer(self._base_broker_url, self.AR_FOREMAN_CONSUME, self._base_msg_format)
        try:
            thread.start_new_thread( self.run_dmcs_consumer, ("thread-dmcs-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start DMCS consumer thread, exiting...')
            sys.exit(99)
        
        self._ar_ctrl_consumer = Consumer(self._base_broker_url, self.AR_CTRL_PUBLISH, self._base_msg_format)
        try:
            thread.start_new_thread( self.run_ar_ctrl_consumer, ("thread-forwarder-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start Archive Ctrl consumer thread, exiting...')
            sys.exit(100)
        
        self._ar_ack_consumer = Consumer(self._base_broker_url, self.AR_FOREMAN_ACK_PUBLISH, self._base_msg_format)
        try:
            thread.start_new_thread( self.run_ar_ack_consumer, ("thread-ncsa-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start NCSA consumer thread, exiting...')
            sys.exit(101)
        

    def run_dmcs_consumer(self, threadname, delay):
        self._dmcs_consumer.run(self.on_dmcs_message)


    def run_ar_ctrl_consumer(self, threadname, delay):
        self._ar_ctrl_consumer.run(self.on_archive_message)


    def run_ar_ack_consumer(self, threadname, delay):
        self._ar_ack_consumer.run(self.on_ack_message)



    def setup_publishers(self):
        LOGGER.info('Setting up Base publisher on %s using %s', self._base_broker_url, self._base_msg_format)
        self._publisher = SimplePublisher(self._base_broker_url, self._base_msg_format)


    def on_dmcs_message(self, ch, method, properties, body):
        #msg_dict = yaml.load(body) 
        msg_dict = body 
        LOGGER.info('In DMCS message callback')
        LOGGER.debug('Thread in DMCS callback is %s', thread.get_ident())
        LOGGER.info('Message from DMCS callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def on_archive_message(self, ch, method, properties, body):
        LOGGER.info('In Forwarder message callback, thread is %s', thread.get_ident())
        LOGGER.debug('Thread in ACK callback is %s', thread.get_ident())
        LOGGER.info('forwarder callback msg body is: %s', str(body))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def on_ack_message(self, ch, method, properties, body):
        msg_dict = body 
        LOGGER.info('In ACK message callback')
        LOGGER.debug('Thread in ACK callback is %s', thread.get_ident())
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
        image_src = params[IMAGE_SRC]
        ccds = params[CCDS]
        start_int_ack_id = params[ACK_ID]

        # next, run health check
        health_check_ack_id = self.get_next_timed_ack('AR_FWDR_HEALTH_ACK')
        num_fwdrs_checked = self.fwdr_health_check(health_check_ack_id)

        # Add job scbd entry
        self.JOB_SCBD.add_job(job_number, image_id, visit_id, ccds)
        self.JOB_SCBD.set_job_params(job_number, {'IMAGE_SRC': image_src, 
                                                  'SESSION_ID': session_id, 
                                                  'VISIT_ID': visit_id})
        self.ack_timer(1.5)

        healthy_fwdrs = self.ACK_SCBD.get_components_for_timed_ack(health_check_ack_id)
        if healthy_fwdrs == None:
            self.refuse_job(params, "No forwarders available")
            self.JOB_SCBD.set_job_state(job_number, 'SCRUBBED')
            self.JOB_SCBD.set_job_status(job_number, 'INACTIVE')
            return

        for forwarder in forwarders:
            self.FWD_SCBD.set_forwarder_state(forwarder, 'BUSY')
            self.FWD_SCBD.set_forwarder_status(forwarder, 'HEALTHY')

        # send new_archive_item msg to archive controller
        ac_timed_ack = self.get_next_timed_ack('AR_CTRL_NEW_ITEM')
        start_int_params['NEW_ARCHIVE_ITEM'] = ac_timed_ack
        start_int_params['ACK_ID'] = ac_timed_ack
        start_int_params['REPLY_QUEUE'] = AR_FOREMAN_ACK_PUBLISH
        self.JOB_SCBD.set_job_state(job_number, 'AR_NEW_ITEM_QUERY')
        self.publisher.publish_message('ARCHIVE_CTRL_CONSUME', start_int_params)
        self.ack_timer(2)
        
        # receive target dir back in ack from AC
        ar_response = self.ACK_SCBD.get_components_for_timed_ack(ac_timed_ack)
        if len(ar_response) < 1:
            start_int_params['ACK_ID'] = start_int__ack_id
            self.refuse_job(start_int_params, "No response from archive")
            scrub_params = {'STATE':'scrubbed', 'STATUS':'INACTIVE'}
            self.JOB_SCBD.set_job_params(job_number, scrub_params)
            fscbd_params = {'STATE':'IDLE', 'STATUS':'HEALTHY'}
            self.FWD_SCBD.set_forwarder_params(healthy_forwarders, fscbd_params)
            return

        if ar_response['AR_CTRL'][ACK_BOOL] == False:
            start_int_params['ACK_ID'] = start_int__ack_id
            self.refuse_job(start_int_params, ar_response['AR_CTRL']['FAIL_DETAILS'])
            scrub_params = {'STATE':'scrubbed', 'STATUS':'INACTIVE'}
            self.JOB_SCBD.set_job_params(job_number, scrub_params)
            fscbd_params = {'STATE':'IDLE', 'STATUS':'HEALTHY'}
            self.FWD_SCBD.set_forwarder_params(healthy_forwarders, fscbd_params)
            return

        target_dir = ['AR_CTRL']['TARGET']
        self.JOB_SCBD.set_job_params(job_number, {'STATE':'AR_NEW_ITEM_RESPONSE', 'TARGET_DIR': dir})
        

        # divide image fetch across forwarders
        work_schedule = self.divide_work(healthy_fwdrs.keys(), ccds)

        # send image_id, target dir, and job, session,visit and work to do to healthy forwarders
        self.JOB_SCBD.set_value_for_job(job_number, { 'STATE':'SENDING_XFER_PARAMS'})
        self.set_ccds_for_job(job_number, work_schedule)
       
        xfer_params_ack_id = self.get_next_timed_ack_id("AR_FWDR_PARAMS_ACK") 
        start_int_params = copy.deepcopy(self.START_INTEGRATION_XFER_PARAMS)
        start_int_params[TARGET] = target_dir
        start_int_params[ACK_ID] = xfer_params_ack_id
        start_int_params[REPLY_QUEUE] = 'AR_FOREMAN_ACK_PUBLISH'
        start_int_params[JOB_NUM] = 'job_number'
        start_int_params['IMAGE_ID'] = image_id
        start_int_params['SESSION_ID'] = session_id
        start_int_params['VISIT_ID'] = visit_id
        start_int_params['IMAGE_SRC'] = image_src
        self.send_xfer_params(start_int_params, work_schedule)



        # receive ack back from forwarders that they have job params
        self.ack_timer(2)
        params_acks = self.ACK_SCBD.get_components_for_timed_ack(xfer_params_ack_id)
        if len(params_acks) != len(healthy_fwdrs):
            #do something...refuse_job?
            pass

        self.JOB_SCBD.set_value_for_job({'STATE':'XFER_PARAMS_SENT'})

        ##################ACCEPT_JOB
        st_int_params['ACK_ID'] = st_int_ack_id
        st_int_params['COMPONENT_NAME'] = 'AR_FOREMAN'
        self.accept_job(st_int_params)
        self.JOB_SCBD.set_value_for_job(job_num, STATE, "JOB_ACCEPTED")
        fscbd_params = {'STATE':'AWAITING_READOUT'}
        self.FWD_SCBD.set_forwarder_params(healthy_forwarders, fscbd_params)



    def fwdr_health_check(self, ack_id):
        msg_params = {}
        msg_params[MSG_TYPE] = 'FORWARDER_HEALTH_CHECK'
        msg_params[ACK_ID] = ack_id
        msg_params[REPLY_QUEUE] = 'AR_FOREMAN_ACK_PUBLISH'

        forwarders = self.FWD_SCBD.return_available_forwarders_list()
        state_status = {"STATE": "HEALTH_CHECK", "STATUS": "UNKNOWN"}
        self.FWD_SCBD.set_forwarder_params(forwarders, state_status)
        for forwarder in forwarders:
            self._publisher.publish_message(self.FWD_SCBD.get_value_for_forwarder(forwarder,"CONSUME_QUEUE"), msg_params)
        return len(forwarders)


    def divide_work(self, fwdrs_list, ccd_list):
        num_fwdrs = len(fwdrs_list)
        num_ccds = len(ccd_list)

        print "Num ccds: %d" % len(ccd_list)

        schedule = {}
        if num_ccds <= num_fwdrs:
            for k in range (0, num_ccds):
                schedule[fwdrs_list[k]] = ccd_list[k]
        else:
            ccds_per_fwdr = len(ccd_list) / (num_fwdrs - 1)
            offset = 0
            for i in range(0, num_fwdrs):
                schedule[fwdrs_list[i]] = []
                for j in range (offset, (ccds_per_fwdr + offset)):
                    if (j) >= num_ccds:
                        break
                    schedule[fwdrs_list[i]].append(ccd_list[j])
                offset = offset + ccds_per_fwdr

        return schedule


    def send_xfer_params(self, params, work_schedule):
        fwdrs = work_schedule.keys()
        for fwdr in fwdrs:
            params[CCD_LIST] = work_schedule[fwdr] 
            route_key = self.FWD_SCBD.get_value_for_forwarder(fwdr, "CONSUME_QUEUE")
            self._publisher.publish_message(route_key, params)


    def accept_job(self, params):
        dmcs_message = {}
        dmcs_message['JOB_NUM'] = params['JOB_NUM']
        dmcs_message[MSG_TYPE] = START_INTEGRATION_ACK
        dmcs_message['ACK_ID'] = params['ACK_ID']
        dmcs_message['SESSION_ID'] = params['SESSION_ID']
        dmcs_message['VISIT_ID'] = params['VISIT_ID']
        dmcs_message['IMAGE_ID'] = params['IMAGE_ID']
        dmcs_message[ACK_BOOL] = True
        dmcs_message['COMPONENT_NAME'] = 'AR_FOREMAN'
        self._base_publisher.publish_message("dmcs_consume", dmcs_message)


    def refuse_job(self, params, fail_details):
        dmcs_message = {}
        dmcs_message[JOB_NUM] = params[JOB_NUM]
        dmcs_message[MSG_TYPE] = START_INTEGRATION_ACK
        dmcs_message['ACK_ID'] = params['ACK_ID']
        dmcs_message['SESSION_ID'] = params['SESSION_ID']
        dmcs_message['VISIT_ID'] = params['VISIT_ID']
        dmcs_message['IMAGE_ID'] = params['IMAGE_ID']
        dmcs_message[ACK_BOOL] = False 
        dmcs_message['COMPONENT_NAME'] = 'AR_FOREMAN'
        self.JOB_SCBD.set_value_for_job(job_num, STATE, "JOB_REFUSED")
        self._base_publisher.publish_message("dmcs_consume", dmcs_message)


    def process_dmcs_readout(self, params):
        readout_ack_id = params[ACK_ID]
        readout_params = copy.deepcopy(params)
        job_number = params[JOB_NUM]
        image_id = params[IMAGE_ID]
        # send readout to forwarders
        self.JOB_SCBD.set_value_for_job(job_number, 'STATE', 'PREPARE_READOUT')
        fwdr_readout_ack = self.get_next_timed_ack("FWDR_READOUT_ACK")
        self.send_readout(readout_params, fwdr_readout_ack)
        self.JOB_SCBD.set_value_for_job(job_number, 'STATE', 'READOUT_STARTED')
        fscbd_params = {'STATE':'READOUT'}
        self.FWD_SCBD.set_forwarder_params(healthy_forwarders, fscbd_params)

        self.ack_timer(20)

        readout_responses = self.ACK_SCBD.get_components_for_timed_ack(fwdr_readout_ack)
        self.process_readout_responses(readout_responses)

    #def process_readout_responses(readout_responses):
        # Prep Job SCBD for results
        # This section creates another yaml'd multi-level dict
        # in the job scbd. It will look like this:
        # job_number ->
        #    WORK_RESULTS ->
        #        forwarder_x ->
        #                   IMAGE_ID:
        #                   CCDS ->
        #                     CCD: ccd_num
        #                     TARGET_DIR:
        #                     FILENAME: None
        #                     CHECKSUM: None
        #                     RECEIPT: None
        #                     ARCHIVE_CHECK: False 

        confirm_ack = self.get_next_timed_ack('AR_ITEMS_XFERD_ACK')
        fwdrs = readout_responses.keys()
        work_confirm_dict = {}
        for fwdr in fwdrs:
            ccds = fwdr.keys
            for ccd in ccds:
                msg = {}
                msg['FILENAME'] = str(ccd['TARGET_DIR'] + ccd['FILENAME'])
                msg['CHECKSUM'] = ccd['CHECKSUM']
                work_confirm_dict[ccd] = msg

        xfer_list_msg = {}
        xfer_list_msg[MSG_TYPE] = 'AR_ITEMS_XFERD'
        xfer_list_msg[ACK_ID] = confirm_ack
        xfer_list_msg['IMAGE_ID'] = image_id
        xfer_list_msg['CCD_LIST'] = work_confirm_dict
        
        self._publisher.publish_message(self.ARCHIVE_CTRL_CONSUME, xfer_list_msg) 
           
        self.ack_timer(4) 

        xfer_check_responses = self.ACK_SCBD.get_components_for_timed_ack(confirm_ack)
        results = xfer_check_responses['ARCHIVE_CONTROLLER']

        ack_msg = {}
        ack_msg['MSG_TYPE'] = 'READOUT_ACK'
        ack_msg['JOB_NUM'] = job_number
        ack_msg['ACK_ID'] = readout_ack_id
        ack_msg['RESULTS_LIST'] = results
        self._publisher.publish_message("dmcs_consume", ack_msg)


                   
    def send_readout(self, params, readout_ack):
        ro_params = {}
        ro_params['JOB_NUM'] = params['JOB_NUM']
        ro_params['SESSION_ID'] = self.get_current_session()
        ro_params['VISIT_ID'] = self.get_current_visit()
        ro_params['IMAGE_ID'] = params['IMAGE_ID']
        ro_params['IMAGE_SRC'] = params['IMAGE_SRC']
        ro_params['ACK_ID'] = readout_ack
        ro_params['REPLY_QUEUE'] = 'AR_FOREMAN_ACK_PUBLISH' 
        work_schedule = self.JOB_SCBD.get_ccds_for_job(job_number)
        fwdrs = work_schedule.keys()
        for fwdr in fwdrs:
            route_key = self.FWD_SCBD.get_value_for_forwarder(fwdr, "CONSUME_QUEUE")
            self._publisher.publish_message(route_key, ro_params)




 
    def process_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)
        

    def get_next_timed_ack(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        return (ack_type + "_" + str(self._next_timed_ack_id).zfill(6))


    def set_session(self, session):
        self.JOB_SCBD.set_session(session)

    def get_current_session(self):
        return self.JOB_SCBD.get_current_session()


    def set_visit(self, visit):
        self.JOB_SCBD.set_visit_id(visit)

    def get_current_visit(self):
        return self.JOB_SCBD.get_current_visit()
        

    def ack_timer(self, seconds):
        sleep(seconds)
        return True

    def purge_broker(self, queues):
        for q in queues:
            cmd = "rabbitmqctl -p /tester purge_queue " + q
            os.system(cmd)


def main():
    logging.basicConfig(filename='logs/BaseForeman.log', level=logging.INFO, format=LOG_FORMAT)
    a_fm = ArchiveDevice()
    print "Beginning ArchiveForeman event loop..."
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print ""
    print "Archive Device Done."



if __name__ == "__main__": main()
