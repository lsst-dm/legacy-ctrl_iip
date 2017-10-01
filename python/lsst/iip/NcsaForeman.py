import toolsmod
from toolsmod import get_timestamp
import logging
import pika
import redis
import yaml
import sys
import os
import time
import _thread
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
LOGGER = logging.getLogger(__name__)


class NcsaForeman:
    NCSA_CONSUME = "ncsa_consume"
    NCSA_PUBLISH = "ncsa_publish"
    DISTRIBUTOR_PUBLISH = "distributor_publish"
    ACK_PUBLISH = "ack_publish"
    CFG_FILE = 'L1SystemCfg.yaml'
    prp = toolsmod.prp


    def __init__(self, filename=None):
        toolsmod.singleton(self)

        self._config_file = self.CFG_FILE
        if filename != None:
            self._config_fie = filename

        #self._pairing_dict = {}

        LOGGER.info('Extracting values from Config dictionary')
        self.extract_config_values()

 

        self._msg_actions = { 'NEXT_VISIT': self.process_next_visit,
                              'NEW_SESSION': self.process_new_session,
                              'NCSA_START_INTEGRATION': self.process_start_integration,
                              'NCSA_READOUT': self.process_readout,
                              'DISTRIBUTOR_HEALTH_ACK': self.process_distributor_health_ack,
                              'DISTRIBUTOR_JOB_PARAMS_ACK': self.process_distributor_job_params_ack,
                              'DISTRIBUTOR_READOUT_ACK': self.process_readout_ack }

        self._next_timed_ack_id = 10000

        self.setup_publishers()

        self.setup_scoreboards()

        self._ncsa_broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._ncsa_broker_addr)
        self._ncsa_broker_clstr_url = "amqp://" + self._clster_name + ":" + self._clstr_passwd + "@" + str(self._ncsa_broker_addr)
        self._ncsa_broker_clstr_pub_url = "amqp://" + self._clstr_pub_name + ":" + self._clstr_pub_passwd + "@" + str(self._ncsa_broker_addr)
        LOGGER.info('Building _broker_url. Result is %s', self._ncsa_broker_url)

        self.setup_publishers()
        self.setup_consumers()

        LOGGER.info('Ncsa foreman consumer setup')
        self.thread_manager = None
        self.setup_consumer_threads()

        LOGGER.info('Ncsa Foreman Init complete')



    def setup_publishers(self):
        self._pub_base_broker_url = "amqp://" + self._pub_name + ":" + \
                                                self._pub_passwd + "@" + \
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





    def setup_consumers(self):
        """This method sets up a message listener from each entity
           with which the BaseForeman has contact here. These
           listeners are instanced in this class, but their run
           methods are each called as a separate thread. While
           pika does not claim to be thread safe, the manner in which 
           the listeners are invoked below is a safe implementation
           that provides non-blocking, fully asynchronous messaging
           to the BaseForeman.

        """
        LOGGER.info('Setting up consumers on %s', self._ncsa_broker_url)
        LOGGER.info('Running start_new_thread on all consumer methods')

        self._ncsa_consumer = Consumer(self._ncsa_broker_url, self.NCSA_CONSUME)
        try:
            _thread.start_new_thread( self.run_ncsa_consumer, ("thread-ncsa-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start NCSA consumer thread, exiting...')
            sys.exit(99)

        self._distributor_consumer = Consumer(self._ncsa_broker_url, self.DISTRIBUTOR_PUBLISH)
        try:
            _thread.start_new_thread( self.run_distributor_consumer, ("thread-distributor-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start DISTRBUTORS consumer thread, exiting...')
            sys.exit(100)

        self._ack_consumer = Consumer(self._ncsa_broker_url, self.ACK_PUBLISH)
        try:
            _thread.start_new_thread( self.run_ack_consumer, ("thread-ack-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start ACK consumer thread, exiting...')
            sys.exit(102)

        LOGGER.info('Finished starting all three consumer threads')


    def run_distributor_consumer(self, threadname, delay):
        self._distributor_consumer.run(self.on_distributor_message)


    def run_ncsa_consumer(self, threadname, delay):
        self._ncsa_consumer.run(self.on_base_message)


    def run_ack_consumer(self, threadname, delay):
        self._ack_consumer.run(self.on_ack_message)




    def setup_federated_exchange(self):
        # Set up connection URL for Base Broker here.
        self._base_broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._base_broker_addr)
        LOGGER.info('Building _base_broker_url. Result is %s', self._base_broker_url)
        pass


    def on_distributor_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag) 
        msg_dict = body 
        LOGGER.info('In Distributor message callback')
        LOGGER.debug('Thread in Distributor callback is %s', _thread.get_ident())
        LOGGER.info('Message from Distributor callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def on_base_message(self,ch, method, properties, body):
        ch.basic_ack(method.delivery_tag) 
        LOGGER.info('In base message callback, thread is %s', _thread.get_ident())
        msg_dict = yaml.load(body)
        LOGGER.info('base msg callback body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def on_ack_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag) 
        msg_dict = yaml.load(body) 
        LOGGER.info('In ACK message callback')
        LOGGER.debug('Thread in ACK callback is %s', _thread.get_ident())
        LOGGER.info('Message from ACK callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def process_start_integration(self, params):
        job_num = str(params[JOB_NUM])
        image_id = params['IMAGE_ID']
        visit_id = params['VISIT_ID']
        response_timed_ack_id = params["ACK_ID"] 
        LOGGER.info('NCSA received Start Integration message from Base')
        LOGGER.debug('NCSA Start Integration incoming message: %s' % pprint.pformat(params))
       
        forwarders_list = params['FORWARDERS']['FORWARDER_LIST']
        ccds_list = params['FORWARDERS']['CCD_LIST'] # A list of lists...
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
            self._publisher.publish_message(self.DIST_SCBD.get_value_for_distributor
                                              (distributor,"CONSUME_QUEUE"), ack_params)
        
        # start timers
        self.ack_timer(2)
 
        # at end of timer, get list of distributors
        healthy_distributors = self.ACK_SCBD.get_components_for_timed_ack(timed_ack)

        # update distributor scoreboard with healthy distributors 
        healthy_status = {"STATUS": "HEALTHY"}
        self.DIST_SCBD.set_distributor_params(healthy_distributors, healthy_status)


        num_healthy_distributors = len(healthy_distributors)
        if needed_workers > num_healthy_distributors:
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
            Pairs = assemble_pairs(forwarders_list, ccds_list, healthy_distributors)

            # Now inform NCSA that all is in ready state
            ncsa_params = {}
            ncsa_params[MSG_TYPE] = "NCSA_START_INTEGRATION_ACK"
            ncsa_params[JOB_NUM] = job_num
            ncsa_params['IMAGE_ID'] = image_id
            ncsa_params['VISIT_ID'] = visit_id
            ncsa_params['SESSION'] params['SESSION']
            ncsa_params['COMPONENT'] = 'NCSA_FOREMAN'
            ncsa_params[ACK_BOOL] = True
            ncsa_params["ACK_ID"] = response_timed_ack_id
            ncsa_params["PAIRS"] = Pairs
            self._base_publisher.publish_message(params['REPLY_QUEUE'], ncsa_params) 
            LOGGER.info('Sufficient distributors and workers are available. Informing Base')
            LOGGER.debug('NCSA Start Integration incoming message: %s' % pprint.pformat(ncsa_params))

            # send pair info to each distributor
            job_params_ack = self.get_next_timed_ack_id(DISTRIBUTOR_JOB_PARAMS_ACK)
            keez = list(pairs_dict.keys())
            for j in range(0, len(Pairs)):
              tmp_msg = {}
              tmp_msg[MSG_TYPE] = DISTRIBUTOR_JOB_PARAMS
              tmp_msg['XFER_PARAMS'] = Pairs[i]
              tmp_msg[JOB_NUM] = job_num
              tmp_msg[ACK_ID] = job_params_ack
              tmp_msg['REPLY_QUEUE'] = 'ncsa_foreman_ack_publish'
              tmp_msg['VISIT_ID'] = visit_id
              tmp_msg['IMAGE_ID'] = image_id
              fqn = Pairs[i]['DISTRIBUTOR']['FQN']
              route_key = self.DIST_SCBD.get_value_for_distributor(fqn, "CONSUME_QUEUE')
              self._publisher.publish_message(route_key, tmp_msg)

            LOGGER.info('The following pairings have been sent to the Base for job %s:' % job_num)
            LOGGER.info(self.prp.pprint.pformat(Pairs))

            self.JOB_SCBD.set_pairs_for_job(job_num, Pairs)                

            self.DIST_SCBD.set_distributor_params(healthy_distributors, {STATE: IN_READY_STATE})

            dist_params_response = self.progressive_ack_timer(job_params_ack, num_healthy_distributors, 2.0)

            if dist_params_response == None:
                pass  #Do something such as raise a system wide exception 


    def assemble_pairs(forwarders_list, ccds_list, healthy_distributors):

        #build dict...
        PAIRS = []

        for i in range (0, len(forwarders_list)):
            tmp_dict = {}
            sub_dict = {}
            tmp_dict['FORWARDER'] = forwarder_list[i]
            tmp_dict['CCD_LIST'] = ccds_list[i]
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
            


    def process_base_readout(self, params):
        job_number = params[JOB_NUM]
        response_ack_id = params[ACK_ID]
        pairs = self.JOB_SCBD.get_pairs_for_job(job_number)
        date = get_timestamp()
        ack_id = self.get_next_timed_ack_id(DISTRIBUTOR_READOUT)
        self.JOB_SCBD.set_value_for_job(job_number, START_READOUT, date) 
        # The following line extracts the distributor FQNs from pairs dict using
        # list comprehension values; faster than for loops
        distributors = [v['FQN'] for v in list(pairs.values())]
        for distributor in distributors:
            msg_params = {}
            msg_params[MSG_TYPE] = DISTRIBUTOR_READOUT
            msg_params[JOB_NUM] = job_number
            msg_params[ACK_ID] = ack_id
            routing_key = self.DIST_SCBD.get_routing_key(distributor)
            self.DIST_SCBD.set_distributor_state(distributor, START_READOUT)
            self._publisher.publish_message(routing_key, yaml.dump(msg_params))


        self.ack_timer(4)

        distributor_responses = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
        if len(distributor_responses) == len(distributors):
            ncsa_params = {}
            ncsa_params[MSG_TYPE] = NCSA_READOUT_ACK
            ncsa_params[JOB_NUM] = job_number
            ncsa_params[ACK_ID] = response_ack_id
            ncsa_params[ACK_BOOL] = True
            self.publisher.publish_message("ncsa_publish", yaml.dump(msg_params))
        else:
            ncsa_params = {}
            ncsa_params[MSG_TYPE] = NCSA_READOUT_ACK
            ncsa_params[JOB_NUM] = job_number
            ncsa_params['COMPONENT_NAME'] = NCSA
            ncsa_params[ACK_ID] = response_ack_id
            ncsa_params[ACK_BOOL] = FALSE
            ncsa_params[EXPECTED_DISTRIBUTOR_ACKS] = len(distributors)
            ncsa_params[RECIEVED_DISTRIBUTOR_ACKS] = len(distributor_responses)
            missing_distributors = {}
            forwarders = list(pairs.keys())
            for forwarder in forwarders:
                if forwarder['MATE'] in distributor_responses:
                    continue
                else:
                    missing_distributors[forwarder[MATE]] = forwarder[RAFT]
            ncsa_params[MISSING_DISTRIBUTORS] = missing_distributors
            self.publisher.publish_message("ncsa_publish", yaml.dump(msg_params))
             


    def process_distributor_health_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)

       
    def process_distributor_job_params_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)
       
 
    def process_readout_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)
        

    def intake_yaml_file(self):
        """This method reads the ForemanCfg.yaml config file
           found in the same directory as the BaseForeman class.
           The config file can list an initial set of forwarders and/or
           distributors, as well as the message broker address, default 
           file transfer values, etc.
    
        """
        try:
            f = open('ForemanCfg.yaml')
        except IOError:
            print("Cant open ForemanCfg.yaml")
            print("Bailing out...")
            sys.exit(99)

        #cfg data map...
        cdm = yaml.safe_load(f)

        try:
            self._xfer_app = cdm[XFER_APP]
        except KeyError as e:
            pass #use default or await reassignment

        try:
            self._xfer_file = cdm[XFER_FILE]
        except KeyError:
            pass #use default or await reassignment

        return cdm


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


    def extract_config_values(self):
        try:
            cdm = toolsmod.intake_yaml_file(self._config_file)
        except IOError as e:
            LOGGER.critical("Unable to find CFG Yaml file %s\n" % self._config_file)
            sys.exit(101)

        try:
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self._ncsa_broker_addr = cdm[ROOT][NCSA_BROKER_ADDR]
            self._ncsa_broker_addr = cdm[ROOT][NCSA_BROKER_ADDR]
            self._ncsa_broker_addr = cdm[ROOT][NCSA_BROKER_ADDR]
            self._sub_name = [ROOT]['NCSA_BROKER_NAME']      # Message broker user & passwd
            self._sub_passwd = [ROOT]['NCSA_BROKER_PASSWD']   
            #### FIX FIX FIX - make work with setu consumer threads method
            self._pub_name = [ROOT]['NCSA_BROKER_PUB_NAME']  
            self._pub_passwd = [ROOT]['NCSA_BROKER_PUB_PASSWD']   
            self._clstr_name = [ROOT]['NCSA_CLSTR']
            self._clstr_passwd = [ROOT]['NCSA_CLSTR']   
            self._clstr_pub_name = [ROOT]['NCSA_CLSTR_PUB']
            self._clstr_pub_passwd = [ROOT]['NCSA_CLSTR_PUB']   
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
        md['amqp_url'] = ncsa_broker_url
        md['name'] = 'Thread-ncsa_foreman_ack_publish'
        md['queue'] = 'ncsa_foreman_ack_publish'
        md['callback'] = self.on_ack_message
        md['format'] = "YAML"
        md['test_val'] = 'test_it'
        kws[md['name']] = md

        md = {}
        md['amqp_url'] = ncsa_broker_url
        md['name'] = 'Thread-ncsa_consume'
        md['queue'] = 'ncsa_consume'
        md['callback'] = self.on_pp_message
        md['format'] = "YAML"
        md['test_val'] = 'test_it'
        kws[md['name']] = md

        self.thread_manager = ThreadManager('thread-manager', kws)
        self.thread_manager.start()

    def setup_scoreboards(self):
        # Create Redis Distributor table with Distributor info
        self.DIST_SCBD = DistributorScoreboard('NCSA_DIST_SCBD', \
                                               self._scbd_dict['NCSA_DIST_SCBD'], \
                                               self.distributor_dict)
        self.JOB_SCBD = JobScoreboard('NCSA_JOB_SCBD', self._scbd_dict['NCSA_JOB_SCBD'])
        self.ACK_SCBD = AckScoreboard('NCSA_ACK_SCBD', self._scbd_dict['NCSA_ACK_SCBD'])



def main():
    logging.basicConfig(filename='logs/NcsaForeman.log', level=logging.INFO, format=LOG_FORMAT)
    n_fm = NcsaForeman()
    print("Beginning BaseForeman event loop...")
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print("")
    print("Ncsa Foreman Done.")


if __name__ == "__main__": main()
