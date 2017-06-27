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
from SimplePublisher import SimplePublisher

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class NcsaForeman:
    DIST_SCBD = None
    JOB_SCBD = None
    ACK_SCBD = None
    NCSA_CONSUME = "ncsa_consume"
    NCSA_PUBLISH = "ncsa_publish"
    ACK_PUBLISH = "ncsa_foreman_ack_publish"
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'direct'


    def __init__(self, filename=None):
        toolsmod.singleton(self)

        self._name = 'NCSA_FM'      # Message broker user & passwd
        self._passwd = 'NCSA_FM'   
        self._base_broker_url = 'amqp_url'
        self._ncsa_broker_url = 'amqp_url'
        self._pairing_dict = {}
        self._next_timed_ack_id = 10000
 
        self._config_file = "L1SystemCfg.yaml"
        if filename != None: 
            self._config_file = filename
        
        cdm = toolsmod.intake_yaml_file(self._config_file)
        try:
            self.job_db_instance = cdm[ROOT]["SCOREBOARDS"]["NCSA_JOB_SCBD"]
            self.ack_db_instance = cdm[ROOT]["SCOREBOARDS"]["NCSA_ACK_SCBD"]
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self._ncsa_broker_addr = cdm[ROOT][NCSA_BROKER_ADDR]
            distributor_dict = cdm[ROOT][XFER_COMPONENTS][DISTRIBUTORS]
        except KeyError as e:
            print("Dictionary error")
            print("Bailing out...")
            sys.exit(99)

        # Create Redis Distributor table with Distributor info

        self.DIST_SCBD = DistributorScoreboard(distributor_dict)
        self.JOB_SCBD = JobScoreboard("NCSA_JOB_SCBD", self.job_db_instance)
        self.ACK_SCBD = AckScoreboard("NCSA_ACK_SCBD", self.ack_db_instance)
        self._msg_actions = { 'NCSA_RESOURCES_QUERY': self.process_base_resources_query,
                              'NCSA_READOUT': self.process_base_readout,
                              'DISTRIBUTOR_HEALTH_ACK': self.process_distributor_health_ack,
                              'DISTRIBUTOR_JOB_PARAMS_ACK': self.process_distributor_job_params_ack,
                              'DISTRIBUTOR_READOUT_ACK': self.process_readout_ack }


        self._ncsa_broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._ncsa_broker_addr)
        LOGGER.info('Building _broker_url. Result is %s', self._ncsa_broker_url)

        self._base_broker_url = self._ncsa_broker_url

        self.setup_publishers()
        self.setup_consumers()

        # self._base_broker_url = "" 
        self.setup_federated_exchange()


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

        self._ack_consumer = Consumer(self._ncsa_broker_url, self.ACK_PUBLISH)
        try:
            _thread.start_new_thread( self.run_ack_consumer, ("thread-ack-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start ACK consumer thread, exiting...')
            sys.exit(102)

        LOGGER.info('Finished starting all three consumer threads')


    def run_ncsa_consumer(self, threadname, delay):
        self._ncsa_consumer.run(self.on_base_message)

    def run_ack_consumer(self, threadname, delay):
        self._ack_consumer.run(self.on_ack_message)


    def setup_publishers(self):
        LOGGER.info('Setting up Base publisher on %s', self._base_broker_url)
        LOGGER.info('Setting up NCSA publisher on %s', self._ncsa_broker_url)

        self._base_publisher = SimplePublisher(self._base_broker_url)
        print(("BASE_PUBLISHER: %s" % self._base_broker_url))
        self._publisher = SimplePublisher(self._ncsa_broker_url)


    def setup_federated_exchange(self):
        # Set up connection URL for Base Broker here.
        self._base_broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._base_broker_addr)
        LOGGER.info('Building _base_broker_url. Result is %s', self._base_broker_url)
        pass


    def on_base_message(self,ch, method, properties, body):
        LOGGER.info('In base message callback, thread is %s', _thread.get_ident())
        msg_dict = body
        LOGGER.info('base msg callback body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def on_ack_message(self, ch, method, properties, body):
        msg_dict = body 
        LOGGER.info('In ACK message callback')
        LOGGER.debug('Thread in ACK callback is %s', _thread.get_ident())
        LOGGER.info('Message from ACK callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    
    def send_health_check(self, timed_ack, params): 
        job_num = str(params[JOB_NUM])
        distributors = self.DIST_SCBD.return_distributors_list()
        
        # Mark all healthy distributors Unknown
        state_unknown = {"STATE": "HEALTH_CHECK", "STATUS": "UNKNOWN"}
        print(("DIST: %s" % distributors))
        self.DIST_SCBD.set_params_for_multiple_distributors(distributors, state_unknown)

        # send health check messages
        ack_params = {}
        ack_params[MSG_TYPE] = "DISTRIBUTOR_HEALTH_CHECK"
        ack_params["ACK_ID"] = timed_ack
        ack_params[JOB_NUM] = job_num
        for distributor in distributors:
            self._publisher.publish_message(self.DIST_SCBD.get_value_for_distributor
                                              (distributor,"CONSUME_QUEUE"), ack_params)
        

    def process_base_resources_query(self, params):
        timed_ack = self.get_next_timed_ack_id("Distributor_Ack")
        job_num = str(params[JOB_NUM])
        LOGGER.info('NCSA received message from Base asking for available resources')#
       
        response_timed_ack_id = params["ACK_ID"] 
        forwarders_dict = params[FORWARDERS]
        needed_workers = len(list(forwarders_dict.keys()))
        self.JOB_SCBD.add_job(job_num, needed_workers, None, None)
        LOGGER.info('Received new job %s. Needed workers is %s', job_num, str(needed_workers))

        self.send_health_check(timed_ack, params)
        # start timers
        self.ack_timer(3) 
        # at end of timer, get list of distributors
        healthy_distributors_dict = self.ACK_SCBD.get_components_for_timed_ack(timed_ack)
        healthy_distributors = list(healthy_distributors_dict.keys())

        print(("HEALTHY_DIST: %s" % healthy_distributors))
        # update distributor scoreboard with healthy distributors 
        healthy_status = {"STATUS": "HEALTHY"}
        self.DIST_SCBD.set_params_for_multiple_distributors(healthy_distributors, healthy_status)

        num_healthy_distributors = len(healthy_distributors)
        if needed_workers > num_healthy_distributors:
            # send response msg to base refusing job
            LOGGER.info('Reporting to base insufficient healthy distributors for job #%s', job_num)
            ncsa_params = {}
            ncsa_params[MSG_TYPE] = "NCSA_RESOURCES_QUERY_ACK"
            ncsa_params[JOB_NUM] = job_num
            ncsa_params["ACK_BOOL"] = False
            ncsa_params["ACK_ID"] = response_timed_ack_id
            ncsa_params[AVAILABLE_DISTRIBUTORS] = str(num_healthy_distributors)
            ncsa_params[AVAILABLE_WORKERS] = str(0)
            self._base_publisher.publish_message(NCSA_PUBLISH, ncsa_params)
            # delete job and leave distributors in Idle state
            self.JOB_SCBD.delete_job(job_num)
            idle_state = {"STATE": "IDLE"}
            self.DIST_SCBD.set_params_for_multiple_distributors(healthy_distributors, idle_state)

        else:
            LOGGER.info('Sufficient distributors and workers are available. Informing NCSA')
            pairs_dict = self.assemble_pairs_dict(forwarders_dict, healthy_distributors)

            print(("PAIRS_DICT: %s" % pairs_dict))

            # send pair info to each distributor
            job_params_ack = self.get_next_timed_ack_id(DISTRIBUTOR_JOB_PARAMS_ACK)
            keez = list(pairs_dict.keys())
            for fwdr in keez:
              tmp_msg = {}
              tmp_msg[MSG_TYPE] = DISTRIBUTOR_JOB_PARAMS
              tmp_msg["TRANSFER_PARAMS"] = fwdr
              tmp_msg[JOB_NUM] = job_num
              tmp_msg[ACK_ID] = job_params_ack
              route_key = self.DIST_SCBD.get_value_for_distributor(pairs_dict[fwdr][FQN], ROUTING_KEY)
              print(("ROUTE_KEY: %s" % route_key))
              self._publisher.publish_message(route_key, tmp_msg)
            
            # Now inform NCSA that all is in ready state
            ncsa_params = {}
            ncsa_params[MSG_TYPE] = "NCSA_RESOURCES_QUERY_ACK"
            ncsa_params[JOB_NUM] = job_num
            ncsa_params[ACK_BOOL] = True
            ncsa_params["ACK_ID"] = response_timed_ack_id
            ncsa_params["PAIRS"] = pairs_dict
            self._base_publisher.publish_message(self.NCSA_PUBLISH, ncsa_params) 

            LOGGER.info('The following pairings have been sent to the Base:')
            LOGGER.info(pairs_dict)

            self.JOB_SCBD.set_pairs_for_job(job_num, pairs_dict)                
            LOGGER.info('The following pairs will be used for Job #%s: %s',job_num, str(pairs_dict))

            self.DIST_SCBD.set_params_for_multiple_distributors(healthy_distributors, {STATE: IN_READY_STATE})

            self.ack_timer(2)

            dist_params_response = self.ACK_SCBD.get_components_for_timed_ack(job_params_ack)
            print(("DIST_PARAMS: %s" % dist_params_response))
            if len(keez) != len(dist_params_response):
                pass  #Do something when a policy is set...maybe async msg to base foreman? 

    def assemble_pairs_dict(self, forwarders_dict, healthy_distributors):
        keez = list(forwarders_dict.keys())

        #build dict...
        pairs_dict = {}

        number_pairs = len(keez)
        for i in range (0, number_pairs):
            tmp_dict = {}
            distributor = healthy_distributors[i]
            tmp_dict['FQN'] = distributor
            tmp_dict['RAFT'] = forwarders_dict[keez[i]]
            tmp_dict['HOSTNAME'] = self.DIST_SCBD.get_value_for_distributor(distributor, HOSTNAME)
            tmp_dict['NAME'] = self.DIST_SCBD.get_value_for_distributor(distributor, NAME)
            tmp_dict['IP_ADDR'] = self.DIST_SCBD.get_value_for_distributor(distributor, IP_ADDR)
            tmp_dict['TARGET_DIR'] = self.DIST_SCBD.get_value_for_distributor(distributor, TARGET_DIR)
            pairs_dict[keez[i]] = tmp_dict

        return pairs_dict
            


    def process_base_readout(self, params):
        job_number = params[JOB_NUM]
        response_ack_id = params[ACK_ID]
        pairs = self.JOB_SCBD.get_pairs_for_job(job_number)
        date = get_timestamp()
        ack_id = self.get_next_timed_ack_id(DISTRIBUTOR_READOUT)
        self.JOB_SCBD.set_value_for_job(job_number, "START_READOUT", date) 
        # The following line extracts the distributor FQNs from pairs dict using
        # list comprehension values; faster than for loops
        distributors = [v['FQN'] for v in list(pairs.values())]
        for distributor in distributors:
            msg_params = {}
            msg_params[MSG_TYPE] = DISTRIBUTOR_READOUT
            msg_params[JOB_NUM] = job_number
            msg_params[ACK_ID] = ack_id
            routing_key = self.DIST_SCBD.get_routing_key(distributor)
            self.DIST_SCBD.set_distributor_state(distributor, "START_READOUT")
            self._publisher.publish_message(routing_key, msg_params)


        self.ack_timer(4)

        distributor_responses = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
        print("DIST_RESPONSE: %s" % distributor_responses)
        if len(distributor_responses) == len(distributors):
            ncsa_params = {}
            ncsa_params[MSG_TYPE] = NCSA_READOUT_ACK
            ncsa_params[JOB_NUM] = job_number
            ncsa_params[ACK_ID] = response_ack_id
            ncsa_params[ACK_BOOL] = True
            self.publisher.publish_message("ncsa_publish", msg_params)
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
            self.publisher.publish_message("ncsa_publish", msg_params)
             


    def process_distributor_health_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)

       
    def process_distributor_job_params_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)
       
 
    def process_readout_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)
        
    def get_next_timed_ack_id(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        retval = ack_type + "_" + str(self._next_timed_ack_id).zfill(6)
        return retval 


    def ack_timer(self, seconds):
        time.sleep(seconds)
        return True


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
