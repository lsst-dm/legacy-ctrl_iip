import toolsmod
import logging
import pika
import redis
import yaml
import sys
import time
import thread
from const import *
from Scoreboard import Scoreboard
from ForwarderScoreboard import ForwarderScoreboard
from DistributorScoreboard import DistributorScoreboard
from JobScoreboard import JobScoreboard
from Consumer import Consumer
from SimplePublisher import SimplePublisher

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class BaseForeman:
    FWD_SCBD = None
    DIST_SCBD = None
    JOB_SCBD = None
    DMCS_PUBLISH = "dmcs_publish"
    DMCS_CONSUME = "dmcs_consume"
    NCSA_PUBLISH = "ncsa_publish"
    FORWARDER_PUBLISH = "forwarder_publish"
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'direct'


    def __init__(self):
        toolsmod.singleton(self)

        self._name = 'FM'      # rabbit user & passwd
        self._passwd = 'FM'   
        self._broker_url = 'amqp_url'
        self._xfer_app = 'rsync'
        self._xfer_file = 'small.fits'
 
        cdm = self.intake_yaml_file()
        try:
            self._broker_addr = cdm[ROOT][BROKER_ADDR]
            forwarder_dict = cdm[ROOT][XFER_COMPONENTS][FORWARDERS]
            distributor_dict = cdm[ROOT][XFER_COMPONENTS][DISTRIBUTORS]
        except KeyError as e:
            print "Dictionary error"
            print "Bailing out..."
            sys.exit(99)

        # Create Redis Forwarder table with Forwarder info

        self.FWD_SCBD = ForwarderScoreboard(forwarder_dict)
        self.DIST_SCBD = DistributorScoreboard(distributor_dict)
        self.JOB_SCBD = JobScoreboard()
        self._msg_actions = { 'JOB': self.process_dmcs_job,
                              'CHECK_HEALTH': self.process_dmcs_check_health,
                              'STANDBY': self.process_dmcs_standby,
                              'SET_XFER_APP': self.process_dmcs_set_xfer_app,
                              'SET_XFER_FILE': self.process_dmcs_set_xfer_file,
                              'READOUT': self.process_dmcs_readout,
                              'INSUFFICIENT_NCSA_RESOURCES': self.process_ncsa_insufficient_resources,
                              'PAIRING': self.process_ncsa_pairings }


        self._broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._broker_addr)
        self.setup_publishers()
        self.setup_consumers()
        #self.setup_federated_exchange()


    def setup_consumers(self):
        """This method sets up a message listener from each enitiy
           with which the BaseForeman has contact here. These
           listeners are instanced in this class, but their run
           methods are each called as a separate thread. While
           pika does not claim to be thread safe, the manner in which 
           the listeners are invoked below is a safe implementation
           that provides non-blocking, fully asynchronous messaging
           to the BaseForeman.

        """
        LOGGER.info('Setting up consumers on %s', self._broker_url)
        LOGGER.info('Running start_new_thread on all consumer methods')

        self._dmcs_consumer = Consumer(self._broker_url, self.DMCS_PUBLISH)
        try:
            thread.start_new_thread( self.run_dmcs_consumer, ("thread-dmcs-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start DMCS consumer thread, exiting...')
            sys.exit(99)

        self._forwarder_consumer = Consumer(self._broker_url, self.FORWARDER_PUBLISH)
        try:
            thread.start_new_thread( self.run_forwarder_consumer, ("thread-forwarder-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start FORWARDERS consumer thread, exiting...')
            sys.exit(100)

        self._ncsa_consumer = Consumer(self._broker_url, self.NCSA_PUBLISH)
        try:
            thread.start_new_thread( self.run_ncsa_consumer, ("thread-ncsa-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start NCSA consumer thread, exiting...')
            sys.exit(101)

        LOGGER.info('Finished starting all three consumer threads')


    def run_dmcs_consumer(self, threadname, delay):
        self._dmcs_consumer.run(self.on_dmcs_message)


    def run_forwarder_consumer(self, threadname, delay):
        self._forwarder_consumer.run(self.on_forwarder_message)


    def run_ncsa_consumer(self, threadname, delay):
        self._ncsa_consumer.run(self.on_ncsa_message)



    def setup_publishers(self):
        LOGGER.info('Setting up publisher on %s', self._broker_url)

        self._publisher = SimplePublisher(self._broker_url)
        #self._publisher.run() 


    def setup_federated_exchange(self):
        pass


    def on_dmcs_message(self, ch, method, properties, body):
        msg_dict = yaml.load(body) 
        LOGGER.info('In DMCS message callback')
        LOGGER.debug('Thread in DMCS callback is %s', thread.get_ident())
        LOGGER.info('DMCS callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict['MSG_TYPE'])
        result = handler(msg_dict)
    

    def on_forwarder_message(self, ch, method, properties, body):
        LOGGER.info('In Forwarder message callback, thread is %s', thread.get_ident())
        LOGGER.info('forwarder callback msg body is: %s', str(body))
        pass

    def on_ncsa_message(self,ch, method, properties, body):
        LOGGER.info('In ncsa message callback, thread is %s', thread.get_ident())
        msg_dict = yaml.load(body)
        LOGGER.info('ncsa msg callback body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


    def process_dmcs_job(self, params):
        needed_workers = int(params[RAFT_NUM])
        job_num = str(params[JOB_NUM])
        self.JOB_SCBD.add_job(job_num, needed_workers, self._xfer_app, self._xfer_file)

        # run forwarder health check
        healthy_forwarders = self.FWD_SCBD.return_healthy_forwarders_list()
        num_healthy_forwarders = len(healthy_forwarders)
        if needed_workers > num_healthy_forwarders:
            # send response msg to dmcs refusing job
            params = {}
            params[MSG_TYPE] = INSUFFICIENT_FORWARDERS
            params[JOB_NUM] = job_num
            params[NEEDED_WORKERS] = str(needed_workers)
            params[AVAILABLE_FORWARDERS] = str(num_healthy_forwarders)
            self._publisher.publish_message("dmcs_consume", yaml.dump(params))
            # delete job and leave Forwarders in Idle state
            self.JOB_SCBD.delete_job(job_num)
            return False
        else:
            for forwarder in healthy_forwarders:
                self.FWD_SCBD.set_forwarder_status(forwarder, NCSA_RESOURCES)
                # Call this method for testing...
                # There should be a message sent to NCSA here asking for available resources
                return self.check_ncsa_resources(job_num, needed_workers, healthy_forwarders)


    def process_dmcs_standby(self, params):
        # tell all forwarders then distributors
        job_num = params[JOB_NUM]
        pairs = self.JOB_SCBD.get_pairs_for_job(str(job_num))
        forwarders = pairs.keys()
        for forwarder in forwarders:
            distributor = pairs[forwarder]
            msg_params = {}
            msg_params[MATE] = distributor
            msg_params[STATE] = STANDBY 
            self.FWD_SCBD.set_forwarder_params(forwarder, params)
            msg_params[MSG_TYPE] = STANDBY
            msg_params[XFER_LOGIN] = self.DIST_SCBD.get_value_for_distributor(distributor, XFER_LOGIN)
            msg_params[TARGET_DIR] = self.DIST_SCBD.get_value_for_distributor(distributor, TARGET_DIR)
            msg_params[JOB_NUM] = job_num
            msg_params[XFER_APP] = self._xfer_app
            msg_params[XFER_FILE] = self._xfer_file
            routing_key = self.FWD_SCBD.get_value_for_forwarder(forwarder, ROUTING_KEY)
            self._publisher.publish_message(routing_key, yaml.dump(msg_params))

        distributors = pairs.values()
        LOGGER.info('Number of distributors here is: %s', str(len(distributors)))
        for distributor in distributors:
            msg_params = {}
            msg_params[MSG_TYPE] = STANDBY
            msg_params[JOB_NUM] = job_num
            routing_key = self.DIST_SCBD.get_value_for_distributor(distributor, ROUTING_KEY)
            self.DIST_SCBD.set_distributor_state(distributor, 'STANDBY')
            LOGGER.info('**** Current distributor is: %s', distributor)
            LOGGER.info('DMCS Standby: Sending standby message to routing_key %s', routing_key) 
            self._publisher.publish_message(routing_key, yaml.dump(msg_params))


    def process_dmcs_check_health(self, params):
        pass

    def process_dmcs_set_xfer_app(self, parsms):
        try:
            self._xfer_app = params[XFER_APP]
        except:
            return False
        return True


    def process_dmcs_set_xfer_file(self, params):
        try:
            self._xfer_file = params[XFER_FILE]
        except:
            return False
        return True


    def process_dmcs_readout(self, params):
        job_number = params[JOB_NUM]
        pairs = self.JOB_SCBD.get_pairs_for_job(job_number)
        date = os.command('date +\"%Y-%m-%d %H:%M:%S.%5N\"')
        self.JOB_SCBD.set_value_for_job(job_number, READOUT_SENT, date) 
        distributors = pairs.values()
        forwarders = pairs.keys()

        for distributor in distributors:
          print "Distributor is %s" % distributor
          msg_params = {}
          msg_params[MSG_TYPE] = READOUT
          msg_params[JOB_NUM] = job_number
          routing_key = self.DIST_SCBD.get_routing_key(distributor)
          self._publisher.publish_message(routing_key, yaml.dump(msg_params))

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
        


    def process_ncsa_pairings(self, params):
        job_num = params[JOB_NUM]
        pairs = params[PAIRS]
        #params = {}  #Do I have to declare this in Python?
        #params[STATE] = READY
        #params[PAIRINGS] = pairs

        # Update Job scoreboard
        self.JOB_SCBD.set_value_for_job(job_num, STATE, READY)
        self.JOB_SCBD.set_pairs_for_job(job_num, pairs)

        # Update Forwarder scoreboard and
        # Contact all Forwarders
        #items = pairs.keys()
        LOGGER.info('Pairs set by NCSA are: %s', str(pairs))

        # Do below after receiving STANDBY instead
        """
        # items are FQN forwarder names
        for item in items:
            params = {}
            params[MATE] = pairs[item]
            params[STATE] = READY 
            self.FWD_SCBD.set_forwarder_params(item, params)

            # Now add job_num, msg_type, app, and file type then send to all forwarders
            params[MSG_TYPE] = READY
            params[JOB_NUM] = job_num
            params[XFER_APP] = self._xfer_app
            params[XFER_FILE] = self._xfer_file
            name = self.FWD_SCBD.get_value(item, NAME)
            routing_key = name + '_consume'
            self._publisher.publish_message(routing_key, yaml.dump(params)
        """     

        # Tell DMCS we are ready
        dmcs_message = {}
        dmcs_message[JOB_NUM] = job_num
        dmcs_message[MSG_TYPE] = IN_READY_STATE
        msg = yaml.dump(dmcs_message) 
        self._publisher.publish_message("dmcs_consume", msg )


    def process_ncsa_insufficient_resources(self, params):
        forwarders = params[FORWARDERS_LIST]
        for forwarder in forwarders:
            self.FWD_SCBD.set_forwarder_state(forwarder, IDLE)
            msg_params = {}
            msg_params[MSG_TYPE] = INSUFFICIENT_NCSA_RESOURCES
            msg_params[JOB_NUM] = params[JOB_NUM]
            msg_params[NEEDED_WORKERS] = params[NEEDED_WORKERS]
            msg_params[AVAILABLE_DISTRIBUTORS] = params[AVAILABLE_DISTRIBUTORS]
            msg_params[AVAILABLE_FORWARDERS] = params[AVAILABLE_FORWARDERS]
            self._publisher.publish_message("dmcs_consume", yaml.dump(msg_params))
            # delete job
            self.JOB_SCBD.delete_job(job_number)
            return False


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
            self._publisher.publish_message("ncsa_publish", yaml.dump(params))
            return True

        else:
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


def main():
    logging.basicConfig(filename='logs/BaseForeman.log', level=logging.INFO, format=LOG_FORMAT)
    b_fm = BaseForeman()
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print ""
    print "Base Foreman Done."


if __name__ == "__main__": main()
