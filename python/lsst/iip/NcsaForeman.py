import toolsmod
from toolsmod import get_timestamp
import logging
import pika
import redis
import yaml
import sys
import os
import time
import thread
from const import *
from Scoreboard import Scoreboard
from DistributorScoreboard import DistributorScoreboard
from JobScoreboard import JobScoreboard
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
    DISTRIBUTOR_PUBLISH = "distributor_publish"
    ACK_PUBLISH = "ack_publish"
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'direct'


    def __init__(self):
        toolsmod.singleton(self)

        self._name = 'NCSA_FM'      # Message broker user & passwd
        self._passwd = 'NCSA_FM'   
        self._base_broker_url = 'amqp_url'
        self._ncsa_broker_url = 'amqp_url'
        self._pairing_dict = {}
        self._next_timed_ack_id = 0
 
        cdm = self.intake_yaml_file()
        try:
            self._base_broker_addr = cdm[ROOT][BROKER_ADDR]
            self._ncsa_broker_addr = cdm[ROOT][NCSA_BROKER_ADDR]
            distributor_dict = cdm[ROOT][XFER_COMPONENTS][DISTRIBUTORS]
        except KeyError as e:
            print "Dictionary error"
            print "Bailing out..."
            sys.exit(99)

        # Create Redis Distributor table with Distributor info

        self.DIST_SCBD = DistributorScoreboard(distributor_dict)
        self.JOB_SCBD = JobScoreboard()
        self.ACK_SCBD = AckScoreboard()
        self._msg_actions = { 'NCSA_RESOURCES_QUERY': self.process_base_resources_query,
                              'NCSA_STANDBY': self.process_base_standby,
                              'NCSA_READOUT': self.process_base_readout,
                              'DISTRIBUTOR_HEALTH_ACK': self.process_distributor_health_ack,
                              'DISTRIBUTOR_STANDBY_ACK': self.process_standby_ack,
                              'DISTRIBUTOR_READOUT_ACK': self.process_readout_ack }


        self._ncsa_broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._ncsa_broker_addr)
        LOGGER.info('Building _broker_url. Result is %s', self._broker_url)

        self.setup_publishers()
        self.setup_consumers()

        self._base_broker_url = "" 
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
            thread.start_new_thread( self.run_ncsa_consumer, ("thread-ncsa-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start NCSA consumer thread, exiting...')
            sys.exit(99)

        self._distributor_consumer = Consumer(self._ncsa_broker_url, self.DISTRIBUTOR_PUBLISH)
        try:
            thread.start_new_thread( self.run_distributor_consumer, ("thread-distributor-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start DISTRBUTORS consumer thread, exiting...')
            sys.exit(100)

        self._ack_consumer = Consumer(self._ncsa_broker_url, self.ACK_PUBLISH)
        try:
            thread.start_new_thread( self.run_ack_consumer, ("thread-ack-consumer", 2,) )
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



    def setup_publishers(self):
        LOGGER.info('Setting up Base publisher on %s', self._broker_url)
        LOGGER.info('Setting up NCSA publisher on %s', self._ncsa_broker_url)

        self._base_publisher = SimplePublisher(self._base_broker_url)
        self._ncsa_publisher = SimplePublisher(self._ncsa_broker_url)
        #self._publisher.run() 


    def setup_federated_exchange(self):
        # Set up connection URL for Base Broker here.
        self._base_broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._base_broker_addr)
        LOGGER.info('Building _base_broker_url. Result is %s', self._base_broker_url)
        pass


    def on_distributor_message(self, ch, method, properties, body):
        msg_dict = yaml.load(body) 
        LOGGER.info('In Distributor message callback')
        LOGGER.debug('Thread in Distributor callback is %s', thread.get_ident())
        LOGGER.info('Message from Distributor callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def on_base_message(self,ch, method, properties, body):
        LOGGER.info('In base message callback, thread is %s', thread.get_ident())
        msg_dict = yaml.load(body)
        LOGGER.info('base msg callback body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def on_ack_message(self, ch, method, properties, body):
        msg_dict = yaml.load(body) 
        LOGGER.info('In ACK message callback')
        LOGGER.debug('Thread in ACK callback is %s', thread.get_ident())
        LOGGER.info('Message from ACK callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def process_base_resources_query(self, params):
        job_num = str(params[JOB_NUM])
        LOGGER.info('Base asking NCSA for available resources')#
       
        response_timed_ack_id = params["TIMED_ACK_ID"] 
        needed_workers = int(params[RAFT_NUM])
        forwarders_dict = params[FORWARDERS]
        self.JOB_SCBD.add_job(job_num, needed_workers)
        LOGGER.info('Received new job %s. Needed workers is %s', job_num, needed_workers)

        # run distributor health check
        # get timed_ack_id
        timed_ack = self.get_next_timed_ack_id("Distributor_Ack")

        distributors = self.DIST_SCBD.return_distributors_list()
        # Mark all healthy distributors Unknown
        state_unknown = {"STATE": "HEALTH_CHECK", "STATUS": "UNKNOWN"}
        self.DIST_SCBD.set_distributor_params(distributors, state_unknown)
        # send health check messages
        ack_params = {}
        ack_params[MSG_TYPE] = "HEALTH_CHECK"
        ack_params["TIMED_ACK_ID"] = timed_ack
        ack_params[JOB_NUM] = job_num
        for distributor in distributors:
            self._publisher.publish_message(self.DIST_SCBD.get_value_for_distributor(distributor,"CONSUME_QUEUE"),
                                            yaml.dump(ack_params))
        
        # start timers
        self.ack_timer(3) 
        # at end of timer, get list of distributors
        healthy_distributors = self.ACK_SCBD.get_components_for_timed_ack(timed_ack)
        # update distributor scoreboard with healthy distributors 
        healthy_status = {"STATUS": "HEALTHY"}
        self.DIST_SCBD.set_distributor_params(healthy_distributors, healthy_status)


        num_healthy_distributors = len(healthy_distributors)
        if needed_workers > num_healthy_distributors:
            # send response msg to base refusing job
            LOGGER.info('Reporting to base that there are insufficient healthy distributors for job #%s', job_num)
            ncsa_params = {}
            ncsa_params[MSG_TYPE] = "NCSA_RESOURCES_QUERY_ACK"
            ncsa_params[JOB_NUM] = job_num
            ncsa_params["ACK_BOOL"] = False
            ncsa_params["TIMED_ACK_ID"] = response_timed_ack_id
            ncsa_params[AVAILABLE_DISTRIBUTORS] = str(num_healthy_distributors)
            ncsa_params[AVAILABLE_WORKERS] = str(0)
            self._publisher.publish_message("ncsa_publish", yaml.dump(ncsa_params))
            # delete job and leave distributors in Idle state
            self.JOB_SCBD.delete_job(job_num)
            idle_state = {"STATE": "IDLE"}
            self.DIST_SCBD.set_distributor_params(healthy_distributors, idle_state)

        else:
            LOGGER.info('Sufficient distributors and workers are available. Informing NCSA')
            pairs_dict = assemble_pairs_dict(forwarders_dict, healthy_distributors)
            ncsa_params = {}
            ncsa_params[MSG_TYPE] = "NCSA_RESOURCES_QUERY_ACK"
            ncsa_params[JOB_NUM] = job_num
            ncsa_params[ACK_BOOL] = True
            ncsa_params["TIMED_ACK_ID"] = response_timed_ack_id
            ncsa_params["PAIRS"] = pairs_dict
            LOGGER.info('The following pairings have been sent to the Base:')
            LOGGER.info(pairs_dict)

            self.JOB_SCBD.set_pairs_for_job(job_num, pairs_dict)                
            LOGGER.info('The following pairs will be used for Job #%s: %s',job_num, str(pairing_dict))

            self.DIST_SCBD.set_distributor_params(healthy_distributors, {'STATE': 'IN_READY_STATE'})
            self._ncsa_publisher.publish_message("ncsa_publish", yaml.dump(ncsa_params)) 


    def assemble_pairs_dict(forwarders_dict, healthy_distributors):
        keez = forwarders_dict.keys()

        #build dict...
        pairs_dict = {}

        number_pairs = len(keez)
        for i in range (0, number_pairs):
            tmp_dict = {}
            distributor = healthy_distributors[i]
            tmp_dict['FQN'] = distributor
            tmp_dict['RAFT'] = forwarders_dict[keez[i]]
            tmp_dict['HOSTNAME'] = self.DIST_SCBD.get_value_for_distributor(distributor, 'HOSTNAME')
            tmp_dict['NAME'] = self.DIST_SCBD.get_value_for_distributor(distributor, 'NAME')
            tmp_dict['IP_ADDR'] = self.DIST_SCBD.get_value_for_distributor(distributor, 'IP_ADDR')
            tmp_dict['TARGET_DIR'] = self.DIST_SCBD.get_value_for_distributor(distributor, 'TARGET_DIR')
            pairs_dict[keez[i]] = tmp_dict

        return pairs_dict
            

    def process_distributor_health_ack(self, params):
        if params[ACK_BOOL] == TRUE:
            self.ACK_SCBD.add_timed_ack(params)
        

    def process_base_standby(self, params):
        # tell all forwarders then distributors
        job_num = params[JOB_NUM]
        pairs = self.JOB_SCBD.get_pairs_for_job(str(job_num))
        forwarders = pairs.keys()
        rev_pairs = {}
        for forwarder in forwarders:
            distributor = pairs[forwarder]
            rev_pairs[distributor] = forwarder
            msg_params = {}
            msg_params[MATE] = distributor
            msg_params[STATE] = STANDBY 
### XXX
### XXX Add new Distributor params that came with the ncsa resource ack msg, 
### XXX thereby making the Distributor scoreboard unnecessary at the base -- only at NCSA
### XXX will it be needed.
### XXX
            self.FWD_SCBD.set_forwarder_params(forwarder, params)
            msg_params[MSG_TYPE] = STANDBY
            msg_params[XFER_LOGIN] = self.DIST_SCBD.get_value_for_distributor(distributor, XFER_LOGIN)
            msg_params[TARGET_DIR] = self.DIST_SCBD.get_value_for_distributor(distributor, TARGET_DIR)
            msg_params[JOB_NUM] = job_num
            msg_params[XFER_APP] = self._xfer_app
            msg_params[XFER_FILE] = self._xfer_file
            routing_key = self.FWD_SCBD.get_value_for_forwarder(forwarder, ROUTING_KEY)
            LOGGER.info('Using routing key %s for forwarder %s message. Msg is %s',
                         routing_key, forwarder, msg_params)
            self._publisher.publish_message(routing_key, yaml.dump(msg_params))
### XXX 
### XXX This section below must move to the NCSA Foreman
### XXX
        distributors = pairs.values()
        LOGGER.info('Number of distributors here is: %s', str(len(distributors)))
        for distributor in distributors:
            msg_params = {}
            msg_params[MSG_TYPE] = STANDBY
            msg_params[MATE] = rev_pairs[distributor]
            msg_params[JOB_NUM] = job_num
            routing_key = self.DIST_SCBD.get_value_for_distributor(distributor, ROUTING_KEY)
            self.DIST_SCBD.set_distributor_state(distributor, 'STANDBY')
            LOGGER.debug('**** Current distributor is: %s', distributor)
            LOGGER.info('DMCS Standby: Sending standby message to routing_key %s', routing_key) 
            LOGGER.info('Using routing key %s for distributor %s message. Msg is %s',
                         routing_key, distributor, msg_params)
            self._publisher.publish_message(routing_key, yaml.dump(msg_params))


    def process_base_readout(self, params):
        job_number = params[JOB_NUM]
        pairs = self.JOB_SCBD.get_pairs_for_job(job_number)
        date = os.system('date +\"%Y-%m-%d %H:%M:%S.%5N\"')
        self.JOB_SCBD.set_value_for_job(job_number, READOUT_SENT, date) 
        distributors = pairs.values()
        forwarders = pairs.keys()
### XXX
### XXX This section must move to NCSA Distributor AND
### XXX also the Base Foreman must wait for ack from NCSA
### XXX so this method must send a response ack
### XXX
        #XXX - Add mate value into msg for distributors, for debug purposes
        for distributor in distributors:
          msg_params = {}
          msg_params[MSG_TYPE] = READOUT
          msg_params[JOB_NUM] = job_number
          routing_key = self.DIST_SCBD.get_routing_key(distributor)
          self.DIST_SCBD.set_distributor_state(distributor, READOUT)
          self._publisher.publish_message(routing_key, yaml.dump(msg_params))
### XXX


        for forwarder in forwarders:
            name = self.FWD_SCBD.get_value_for_forwarder(forwarder, NAME)
            routing_key = self.FWD_SCBD.get_routing_key(forwarder)
            msg_params = {}
            msg_params[MSG_TYPE] = READOUT
            msg_params[JOB_NUM] = job_number
            target_dir = self.DIST_SCBD.get_value_for_distributor(pairs[forwarder], TARGET_DIR)
            msg_params[TARGET_DIR] = target_dir
            self.FWD_SCBD.set_forwarder_state(forwarder, READOUT)
            self._publisher.publish_message(routing_key, yaml.dump(msg_params))
        


    def process_standby_ack(self, params):
        if params[MSG_TYPE] == "NCSA_RESOURCES_QUERY_ACK" and params[ACK_BOOL] == TRUE:
           self._pairing_dict = params[PAIRS] 
        self.ACK_SCBD.add_timed_ack(params)
        
    def process_readout_ack(self, params):
        if params[MSG_TYPE] == "NCSA_RESOURCES_QUERY_ACK" and params[ACK_BOOL] == TRUE:
           self._pairing_dict = params[PAIRS] 
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
            print "Cant open ForemanCfg.yaml"
            print "Bailing out..."
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


    def check_ncsa_resources(self, job_number, needed_workers, healthy_forwarders):
        """This is a junk method used only for testing

        """
        LOGGER.info('Checking NCSA Resources')
        pairs = {}
        healthy_distributors = self.DIST_SCBD.get_healthy_distributors_list()
        LOGGER.debug('Healthy dist list returned is %s', healthy_distributors)

        if len(healthy_distributors) >= len(healthy_forwarders):
            # Just pair 'em up...
            number_pairs = len(healthy_forwarders)
            for i in range (0,number_pairs):
                pairs[healthy_forwarders[i]] = healthy_distributors[i]
                self.DIST_SCBD.set_distributor_status(healthy_distributors[i], READY)

            params = {}
            params[MSG_TYPE] = PAIRING
            params[JOB_NUM] = job_number
            params[PAIRS] = pairs
            LOGGER.info('NCSA found adequate number of distributors')
            LOGGER.info('Pairings returned by NCSA:')
            LOGGER.info(pairs)
            self._publisher.publish_message("ncsa_publish", yaml.dump(params))
            return True

        else:
            LOGGER.info('NCSA reports insufficient resources...found only %s distributors', 
                         str(len(healthy_distributors))) 
            params = {}
            params[MSG_TYPE] = INSUFFICIENT_NCSA_RESOURCES
            params[JOB_NUM] = job_number
            params[NEEDED_WORKERS] = needed_workers
            params[AVAILABLE_DISTRIBUTORS] = len(healthy_distributors)
            params[AVAILABLE_FORWARDERS] = len(healthy_forwarders)
            params[FORWARDERS_LIST] = healthy_forwarders
            self._publisher.publish_message("ncsa_publish", yaml.dump(params))
            # delete job 
            self.JOB_SCBD.delete_job(job_number)
            return False


    def get_next_timed_ack_id(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        retval = ack_type + "_" + str(self._next_timed_ack_id).zfill(6)
        return retval 


    def ack_timer(self, seconds):
        sleep(seconds)
        return True


def main():
    logging.basicConfig(filename='logs/BaseForeman.log', level=logging.INFO, format=LOG_FORMAT)
    b_fm = BaseForeman()
    print "Beginning BaseForeman event loop..."
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print ""
    print "Base Foreman Done."


if __name__ == "__main__": main()
