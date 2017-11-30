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
import threading
from const import *
from Scoreboard import Scoreboard
from DistributorScoreboard import DistributorScoreboard
from JobScoreboard import JobScoreboard
from AckScoreboard import AckScoreboard
from Consumer import Consumer
from ThreadManager import ThreadManager
from SimplePublisher import SimplePublisher

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(filename='logs/NcsaForeman.log', level=logging.INFO, format=LOG_FORMAT)
LOGGER = logging.getLogger(__name__)


class NcsaForeman(BaseMgmt):
    NCSA_CONSUME = "ncsa_consume"
    NCSA_PUBLISH = "ncsa_publish"
    COMPONENT_NAME = 'NCSA_FOREMAN'
    DISTRIBUTOR_PUBLISH = "distributor_publish"
    ACK_PUBLISH = "ack_publish"
    CFG_FILE = 'L1SystemCfg.yaml'
    prp = toolsmod.prp


    def __init__(self, filename=None):
        toolsmod.singleton(self)

        self._config_file = self.CFG_FILE
        if filename != None:
            self._config_file = filename

        #self._pairing_dict = {}

        LOGGER.info('Extracting values from Config dictionary')
        self.extract_config_values()

 

        self._msg_actions = { 'NCSA_NEXT_VISIT': self.set_visit,
                              'NCSA_NEW_SESSION': self.set_session,
                              'NCSA_START_INTEGRATION': self.process_start_integration,
                              'NCSA_READOUT': self.process_readout,
                              'DISTRIBUTOR_HEALTH_CHECK_ACK': self.process_ack,
                              'DISTRIBUTOR_XFER_PARAMS_ACK': self.process_ack,
                              'DISTRIBUTOR_READOUT_ACK': self.process_ack }

        self._next_timed_ack_id = 10000

        self.setup_publishers()

        self.setup_scoreboards()

        self.setup_publishers()
        self.setup_consumer_threads()

        LOGGER.info('Ncsa foreman consumer setup')
        self.thread_manager = None
        self.setup_consumer_threads()

        LOGGER.info('Ncsa Foreman Init complete')



    def setup_publishers(self):
        self._pub_base_broker_url = "amqp://" + self._pub_base_name + ":" + \
                                                self._pub_base_passwd + "@" + \
                                                str(self._base_broker_addr)

        self._pub_ncsa_broker_url = "amqp://" + self._pub_ncsa_name + ":" + \
                                                self._pub_ncsa_passwd + "@" + \
                                                str(self._ncsa_broker_addr)

        LOGGER.info('Setting up Base publisher on %s using %s', \
                     self._pub_base_broker_url, self._base_msg_format)
        self._base_publisher = SimplePublisher(self._pub_base_broker_url, self._base_msg_format)

        LOGGER.info('Setting up NCSA publisher on %s using %s', \
                     self._pub_ncsa_broker_url, self._ncsa_msg_format)
        self._ncsa_publisher = SimplePublisher(self._pub_ncsa_broker_url, self._ncsa_msg_format)


    def on_pp_message(self,ch, method, properties, body):
        ch.basic_ack(method.delivery_tag) 
        msg_dict = body
        LOGGER.debug('Message from PP callback message body is: %s', self.prp.pformat(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


    def on_ack_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag) 
        msg_dict = body 
        LOGGER.info('In ACK message callback')
        LOGGER.debug('Message from ACK callback message body is: %s', self.prp.pformat(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


    def set_visit(self, params):
        bore_sight = params['BORE_SIGHT']
        visit_id = params['VISIT_ID']
        self.JOB_SCBD.set_visit_id(visit_id, bore_sight)
        ack_id = params['ACK_ID']
        msg = {}
        ###
        ### Send Boresight to Someone here...
        ###
        msg['MSG_TYPE'] = 'NCSA_NEXT_VISIT_ACK'
        msg['COMPONENT'] = self.COMPONENT_NAME
        msg['ACK_ID'] = ack_id
        msg['ACK_BOOL'] = True
        route_key = params['REPLY_QUEUE']
        self._base_publisher.publish_message(route_key, msg)    


    def set_session(self, params):
        self.JOB_SCBD.set_session(params['SESSION_ID'])
        ack_id = params['ACK_ID']
        msg = {}
        msg['MSG_TYPE'] = 'NCSA_NEW_SESSION_ACK'
        msg['COMPONENT'] = self.COMPONENT_NAME
        msg['ACK_ID'] = ack_id
        msg['ACK_BOOL'] = True
        route_key = params['REPLY_QUEUE']
        self._base_publisher.publish_message(route_key, msg)


    def process_start_integration(self, params):
        job_num = str(params[JOB_NUM])
        image_id = params['IMAGE_ID']
        visit_id = params['VISIT_ID']
        response_timed_ack_id = params["ACK_ID"] 
        LOGGER.info('NCSA received Start Integration message from Base')
        LOGGER.debug('NCSA Start Integration incoming message: %s' % params)
       
        forwarders_list = params['FORWARDERS']['FORWARDER_LIST']
        ccd_list = params['FORWARDERS']['CCD_LIST'] # A list of lists...
        len_forwarders_list = len(forwarders_list)
        self.JOB_SCBD.add_job(job_num, image_id, visit_id, ccd_list)
        LOGGER.info('Received new job %s. Needed workers is %s', job_num, str(len_forwarders_list))

        # run distributor health check
        # get timed_ack_id
        timed_ack = self.get_next_timed_ack_id("DISTRIBUTOR_HEALTH_CHECK_ACK")

        distributors = self.DIST_SCBD.return_distributors_list()
        # Mark all healthy distributors Unknown
        state_unknown = {"STATE": "HEALTH_CHECK", "STATUS": "UNKNOWN"}
        self.DIST_SCBD.set_distributor_params(distributors, state_unknown)

        # send health check messages
        ack_params = {}
        ack_params[MSG_TYPE] = "DISTRIBUTOR_HEALTH_CHECK"
        ack_params['REPLY_QUEUE'] = 'ncsa_foreman_ack_publish'
        ack_params["ACK_ID"] = timed_ack
        ack_params[JOB_NUM] = job_num
        for distributor in distributors:
            self._ncsa_publisher.publish_message(self.DIST_SCBD.get_value_for_distributor
                                              (distributor,"CONSUME_QUEUE"), ack_params)
        
        # start timers
        self.ack_timer(2)
 
        # at end of timer, get list of distributors
        dicts_of_distributors = self.ACK_SCBD.get_components_for_timed_ack(timed_ack)
        healthy_distributors = list(dicts_of_distributors.keys())

        # update distributor scoreboard with healthy distributors 
        healthy_status = {"STATUS": "HEALTHY"}
        self.DIST_SCBD.set_distributor_params(healthy_distributors, healthy_status)


        num_healthy_distributors = len(healthy_distributors)
        if len_forwarders_list > num_healthy_distributors:
            print("Cannot Do Job - more fwdrs than dists")
            # send response msg to base refusing job
            LOGGER.info('Reporting to base insufficient healthy distributors for job #%s', job_num)
            ncsa_params = {}
            ncsa_params[MSG_TYPE] = "NCSA_RESOURCES_QUERY_ACK"
            ncsa_params[JOB_NUM] = job_num
            ncsa_params["ACK_BOOL"] = False
            ncsa_params["ACK_ID"] = response_timed_ack_id
            self._base_publisher.publish_message(NCSA_PUBLISH, yaml.dump(ncsa_params))
            # delete job and leave distributors in Idle state
            self.JOB_SCBD.delete_job(job_num)
            idle_state = {"STATE": "IDLE"}
            self.DIST_SCBD.set_distributor_params(healthy_distributors, idle_state)

        else:
            Pairs = self.assemble_pairs(forwarders_list, ccd_list, healthy_distributors)
            self.JOB_SCBD.set_pairs_for_job(job_num, Pairs)                

            # send pair info to each distributor
            job_params_ack = self.get_next_timed_ack_id('DISTRIBUTOR_XFER_PARAMS_ACK')
            for j in range(0, len(Pairs)):
              tmp_msg = {}
              tmp_msg[MSG_TYPE] = 'DISTRIBUTOR_XFER_PARAMS'
              tmp_msg['XFER_PARAMS'] = Pairs[j]
              tmp_msg[JOB_NUM] = job_num
              tmp_msg[ACK_ID] = job_params_ack
              tmp_msg['REPLY_QUEUE'] = 'ncsa_foreman_ack_publish'
              tmp_msg['VISIT_ID'] = visit_id
              tmp_msg['IMAGE_ID'] = image_id
              fqn = Pairs[j]['DISTRIBUTOR']['FQN']
              route_key = self.DIST_SCBD.get_value_for_distributor(fqn, 'CONSUME_QUEUE')
              self._ncsa_publisher.publish_message(route_key, tmp_msg)

            self.DIST_SCBD.set_distributor_params(healthy_distributors, {STATE: IN_READY_STATE})
            dist_params_response = self.progressive_ack_timer(job_params_ack, num_healthy_distributors, 2.0)

            if dist_params_response == None:
                print("RECEIVED NO ACK RESPONSES FROM DISTRIBUTORS AFTER SENDING XFER PARAMS")
                pass  #Do something such as raise a system wide exception 



            # Now inform PP Foreman that all is in ready state
            ncsa_params = {}
            ncsa_params[MSG_TYPE] = "NCSA_START_INTEGRATION_ACK"
            ncsa_params[JOB_NUM] = job_num
            ncsa_params['IMAGE_ID'] = image_id
            ncsa_params['VISIT_ID'] = visit_id
            ncsa_params['SESSION_ID'] = params['SESSION_ID']
            ncsa_params['COMPONENT'] = 'NCSA_FOREMAN'
            ncsa_params[ACK_BOOL] = True
            ncsa_params["ACK_ID"] = response_timed_ack_id
            ncsa_params["PAIRS"] = Pairs
            self._base_publisher.publish_message(params['REPLY_QUEUE'], ncsa_params) 
            LOGGER.info('Sufficient distributors and workers are available. Informing Base')
            LOGGER.debug('NCSA Start Integration incoming message: %s' % ncsa_params)

            LOGGER.info('The following pairings have been sent to the Base for job %s:' % job_num)
            LOGGER.info(Pairs)


    def assemble_pairs(self, forwarders_list, ccd_list, healthy_distributors):

        #build dict...
        PAIRS = []

        for i in range (0, len(forwarders_list)):
            tmp_dict = {}
            sub_dict = {}
            tmp_dict['FORWARDER'] = forwarders_list[i]
            tmp_dict['CCD_LIST'] = ccd_list[i]
            tmp_dict['DISTRIBUTOR'] = {}
            distributor = healthy_distributors[i]
            sub_dict['FQN'] = distributor
            sub_dict['HOSTNAME'] = self.DIST_SCBD.get_value_for_distributor(distributor, HOSTNAME)
            sub_dict['NAME'] = self.DIST_SCBD.get_value_for_distributor(distributor, NAME)
            sub_dict['IP_ADDR'] = self.DIST_SCBD.get_value_for_distributor(distributor, IP_ADDR)
            sub_dict['TARGET_DIR'] = self.DIST_SCBD.get_value_for_distributor(distributor, TARGET_DIR)
            tmp_dict['DISTRIBUTOR'] = sub_dict
            PAIRS.append(tmp_dict)

        return PAIRS
            


    def process_readout(self, params):
        job_number = params[JOB_NUM]
        response_ack_id = params[ACK_ID]
        pairs = self.JOB_SCBD.get_pairs_for_job(job_number)
        sleep(3)
        len_pairs = len(pairs)
        ack_id = self.get_next_timed_ack_id(DISTRIBUTOR_READOUT_ACK)
        # The following line extracts the distributor FQNs from pairs dict using
        # list comprehension values; faster than for loops
        # distributors = [v['FQN'] for v in list(pairs.values())]
        for i in range(0, len_pairs):  # Pairs is a list of dictionaries
            distributor = pairs[i]['DISTRIBUTOR']['FQN']
            msg_params = {}
            msg_params[MSG_TYPE] = DISTRIBUTOR_READOUT
            msg_params[JOB_NUM] = job_number
            msg_params['REPLY_QUEUE'] = 'ncsa_foreman_ack_publish'
            msg_params[ACK_ID] = ack_id
            routing_key = self.DIST_SCBD.get_routing_key(distributor)
            self.DIST_SCBD.set_distributor_state(distributor, 'START_READOUT')
            self._ncsa_publisher.publish_message(routing_key, msg_params)

        distributor_responses = self.progressive_ack_timer(ack_id, len_pairs, 24)

        if distributor_responses != None:
            RESULT_LIST = {}
            CCD_LIST = []
            RECEIPT_LIST = []
            ncsa_params = {}
            ncsa_params[MSG_TYPE] = NCSA_READOUT_ACK
            ncsa_params[JOB_NUM] = job_number
            ncsa_params['IMAGE_ID'] = params['IMAGE_ID']
            ncsa_params['VISIT_ID'] = params['VISIT_ID']
            ncsa_params['SESSION_ID'] = params['SESSION_ID']
            ncsa_params['COMPONENT'] = 'NCSA_FOREMAN'
            ncsa_params[ACK_ID] = response_ack_id
            ncsa_params[ACK_BOOL] = True
            distributors = list(distributor_responses.keys())
            for dist in distributors:
              ccd_list = distributor_responses[dist]['RESULT_LIST']['CCD_LIST']
              receipt_list = distributor_responses[dist]['RESULT_LIST']['RECEIPT_LIST']
              for i in range (0, len(ccd_list)):
                  CCD_LIST.append(ccd_list[i])
                  RECEIPT_LIST.append(receipt_list[i])
            RESULT_LIST['CCD_LIST'] = CCD_LIST
            RESULT_LIST['RECEIPT_LIST'] = RECEIPT_LIST
            ncsa_params['RESULT_LIST'] = RESULT_LIST
            self._base_publisher.publish_message(params['REPLY_QUEUE'], msg_params)

        else:
            ncsa_params = {}
            ncsa_params[MSG_TYPE] = NCSA_READOUT_ACK
            ncsa_params[JOB_NUM] = job_number
            ncsa_params['COMPONENT_NAME'] = NCSA_FOREMAN
            ncsa_params['IMAGE_ID'] = params['IMAGE_ID']
            ncsa_params['VISIT_ID'] = params['VISIT_ID']
            ncsa_params['SESSION_ID'] = params['SESSION_ID']
            ncsa_params[ACK_ID] = response_ack_id
            ncsa_params[ACK_BOOL] = FALSE
            ncsa_params['RESULT_LIST'] = {}
            ncsa_params['RESULT_LIST']['CCD_LIST'] = None
            ncsa_params['RESULT_LIST']['RECEIPT_LIST'] = None
            self._base_publisher.publish_message(params['REPLY_QUEUE'], msg_params)
             

    def process_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)


    def get_next_timed_ack_id(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        retval = ack_type + "_" + str(self._next_timed_ack_id).zfill(6)
        return retval 


    def ack_timer(self, seconds):
        sleep(seconds)
        return True

    def progressive_ack_timer(self, ack_id, expected_replies, seconds):
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
        try:
            cdm = toolsmod.intake_yaml_file(self._config_file)
        except IOError as e:
            LOGGER.critical("Unable to find CFG Yaml file %s\n" % self._config_file)
            sys.exit(101)

        try:
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self._ncsa_broker_addr = cdm[ROOT][NCSA_BROKER_ADDR]
 
            self._sub_base_name = cdm[ROOT]['NFM_BASE_BROKER_NAME']      # Message broker user & passwd
            self._sub_base_passwd = cdm[ROOT]['NFM_BASE_BROKER_PASSWD']   
            self._sub_ncsa_name = cdm[ROOT]['NFM_NCSA_BROKER_NAME']      # Message broker user & passwd
            self._sub_ncsa_passwd = cdm[ROOT]['NFM_NCSA_BROKER_PASSWD']   

            self._pub_base_name = cdm[ROOT]['BASE_BROKER_PUB_NAME']  
            self._pub_base_passwd = cdm[ROOT]['BASE_BROKER_PUB_PASSWD']   
            self._pub_ncsa_name = cdm[ROOT]['NCSA_BROKER_PUB_NAME']  
            self._pub_ncsa_passwd = cdm[ROOT]['NCSA_BROKER_PUB_PASSWD']

            self._scbd_dict = cdm[ROOT]['SCOREBOARDS'] 
            self.distributor_dict = cdm[ROOT][XFER_COMPONENTS][DISTRIBUTORS]
        except KeyError as e:
            LOGGER.critical("CDM Dictionary error - missing Key")
            LOGGER.critical("Offending Key is %s", str(e))
            LOGGER.critical("Bailing Out...")
            sys.exit(99)

        self._base_msg_format = 'YAML'
        self._ncsa_msg_format = 'YAML'

        if 'BASE_MSG_FORMAT' in cdm[ROOT]:
            self._base_msg_format = cdm[ROOT][BASE_MSG_FORMAT]

        if 'NCSA_MSG_FORMAT' in cdm[ROOT]:
            self._ncsa_msg_format = cdm[ROOT][NCSA_MSG_FORMAT]



    def setup_consumer_threads(self):
        LOGGER.info('Building _base_broker_url')
        base_broker_url = "amqp://" + self._sub_base_name + ":" + \
                                            self._sub_base_passwd + "@" + \
                                            str(self._base_broker_addr)

        ncsa_broker_url = "amqp://" + self._sub_ncsa_name + ":" + \
                                            self._sub_ncsa_passwd + "@" + \
                                            str(self._ncsa_broker_addr)

        #self.shutdown_event = threading.Event()

        # Set up kwargs that describe consumers to be started
        # The Archive Device needs three message consumers
        kws = {}
        md = {}
        md['amqp_url'] = ncsa_broker_url
        md['name'] = 'Thread-ncsa_foreman_ack_publish'
        md['queue'] = 'ncsa_foreman_ack_publish'
        md['callback'] = self.on_ack_message
        md['format'] = "YAML"
        md['test_val'] = 'test_it'
        kws[md['name']] = md

        md = {}
        md['amqp_url'] = base_broker_url
        md['name'] = 'Thread-ncsa_consume'
        md['queue'] = 'ncsa_consume'
        md['callback'] = self.on_pp_message
        md['format'] = "YAML"
        md['test_val'] = 'test_it'
        kws[md['name']] = md

	super(NcsaForeman, self).__init__()
        self.thread_manager = ThreadManager('thread-manager', kws, self.shutdown_event)
        self.thread_manager.start()


    def setup_scoreboards(self):
        # Create Redis Distributor table with Distributor info
        self.DIST_SCBD = DistributorScoreboard('NCSA_DIST_SCBD', \
                                               self._scbd_dict['NCSA_DIST_SCBD'], \
                                               self.distributor_dict)
        self.JOB_SCBD = JobScoreboard('NCSA_JOB_SCBD', self._scbd_dict['NCSA_JOB_SCBD'])
        self.ACK_SCBD = AckScoreboard('NCSA_ACK_SCBD', self._scbd_dict['NCSA_ACK_SCBD'])


   # def shutdown(self):
   #     LOGGER.debug("NCSA Foreman: Shutting down Consumer threads.")
   #     self.shutdown_event.set()
   #     LOGGER.debug("Thread Manager shutting down and app exiting...")
   #     print("\n")
   #     os._exit(0)


def main():
    logging.basicConfig(filename='logs/NcsaForeman.log', level=logging.INFO, format=LOG_FORMAT)
    n_fm = NcsaForeman()
    print("Beginning BaseForeman event loop...")
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        n_fm.shutdown()
        pass

    print("")
    print("Ncsa Foreman Done.")


if __name__ == "__main__": main()
