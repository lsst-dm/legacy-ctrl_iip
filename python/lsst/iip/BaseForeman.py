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


class BaseForeman:
    FWD_SCBD = None
    JOB_SCBD = None
    ACK_SCBD = None
    DMCS_PUBLISH = "dmcs_publish"
    DMCS_CONSUME = "dmcs_consume"
    NCSA_PUBLISH = "ncsa_publish"
    NCSA_CONSUME = "ncsa_consume"
    FORWARDER_PUBLISH = "forwarder_publish"
    ACK_PUBLISH = "ack_publish"
    YAML = 'YAML'
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'direct'


    def __init__(self, filename=None):
        toolsmod.singleton(self)

        self._config_file = 'ForemanCfg.yaml'
        if filename != None:
            self._config_file = filename

        cdm = self.intake_yaml_file(self._config_file)

        try:
            self._base_name = cdm[ROOT][BASE_BROKER_NAME]      # Message broker user & passwd
            self._base_passwd = cdm[ROOT][BASE_BROKER_PASSWD]   
            self._ncsa_name = cdm[ROOT][NCSA_BROKER_NAME]     
            self._ncsa_passwd = cdm[ROOT][NCSA_BROKER_PASSWD]   
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self._ncsa_broker_addr = cdm[ROOT][NCSA_BROKER_ADDR]
            forwarder_dict = cdm[ROOT][XFER_COMPONENTS][FORWARDERS]
        except KeyError as e:
            print "Dictionary error"
            print "Bailing out..."
            sys.exit(99)

        if 'QUEUE_PURGES' in cdm[ROOT]:
            self.purge_broker(cdm['ROOT']['QUEUE_PURGES'])

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

        self.FWD_SCBD = ForwarderScoreboard(forwarder_dict)
        self.JOB_SCBD = JobScoreboard()
        self.ACK_SCBD = AckScoreboard()
        self._msg_actions = { 'NEW_JOB': self.process_dmcs_new_job,
                              'READOUT': self.process_dmcs_readout,
                              'NCSA_RESOURCE_QUERY_ACK': self.process_ack,
                              'NCSA_STANDBY_ACK': self.process_ack,
                              'NCSA_READOUT_ACK': self.process_ack,
                              'FORWARDER_HEALTH_ACK': self.process_ack,
                              'FORWARDER_JOB_PARAMS_ACK': self.process_ack,
                              'FORWARDER_READOUT_ACK': self.process_ack,
                              'NEW_JOB_ACK': self.process_ack }


        self._base_broker_url = "amqp://" + self._base_name + ":" + self._base_passwd + "@" + str(self._base_broker_addr)
        self._ncsa_broker_url = "amqp://" + self._ncsa_name + ":" + self._ncsa_passwd + "@" + str(self._ncsa_broker_addr)
        LOGGER.info('Building _base_broker_url. Result is %s', self._base_broker_url)
        LOGGER.info('Building _ncsa_broker_url. Result is %s', self._ncsa_broker_url)

        self.setup_publishers()
        self.setup_consumers()

        #self._ncsa_broker_url = "" 
        #self.setup_federated_exchange()


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

        self._dmcs_consumer = Consumer(self._base_broker_url, self.DMCS_PUBLISH, self._base_msg_format)
        try:
            thread.start_new_thread( self.run_dmcs_consumer, ("thread-dmcs-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start DMCS consumer thread, exiting...')
            sys.exit(99)

        self._forwarder_consumer = Consumer(self._base_broker_url, self.FORWARDER_PUBLISH, self._base_msg_format)
        try:
            thread.start_new_thread( self.run_forwarder_consumer, ("thread-forwarder-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start FORWARDERS consumer thread, exiting...')
            sys.exit(100)

        self._ncsa_consumer = Consumer(self._base_broker_url, self.NCSA_PUBLISH, self._base_msg_format)
        try:
            thread.start_new_thread( self.run_ncsa_consumer, ("thread-ncsa-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start NCSA consumer thread, exiting...')
            sys.exit(101)

        self._ack_consumer = Consumer(self._base_broker_url, self.ACK_PUBLISH, self._base_msg_format)
        try:
            thread.start_new_thread( self.run_ack_consumer, ("thread-ack-consumer", 2,) )
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
        self._base_publisher = SimplePublisher(self._base_broker_url, self._base_msg_format)
        self._ncsa_publisher = SimplePublisher(self._ncsa_broker_url, self._ncsa_msg_format)


#    def setup_federated_exchange(self):
#        # Set up connection URL for NCSA Broker here.
#        self._ncsa_broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._ncsa_broker_addr)
#        LOGGER.info('Building _ncsa_broker_url. Result is %s', self._ncsa_broker_url)
#        pass


    def on_dmcs_message(self, ch, method, properties, body):
        #msg_dict = yaml.load(body) 
        msg_dict = body 
        LOGGER.info('In DMCS message callback')
        LOGGER.debug('Thread in DMCS callback is %s', thread.get_ident())
        LOGGER.info('Message from DMCS callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def on_forwarder_message(self, ch, method, properties, body):
        LOGGER.info('In Forwarder message callback, thread is %s', thread.get_ident())
        LOGGER.info('forwarder callback msg body is: %s', str(body))
        pass

    def on_ncsa_message(self,ch, method, properties, body):
        LOGGER.info('In ncsa message callback, thread is %s', thread.get_ident())
        #msg_dict = yaml.load(body)
        msg_dict = body
        LOGGER.info('ncsa msg callback body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def on_ack_message(self, ch, method, properties, body):
        msg_dict = body 
        LOGGER.info('In ACK message callback')
        LOGGER.debug('Thread in ACK callback is %s', thread.get_ident())
        LOGGER.info('Message from ACK callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def process_dmcs_new_job(self, params):
        input_params = params
        needed_workers = len(input_params[RAFTS])
        ack_id = self.forwarder_health_check(input_params)
        
        self.ack_timer(7)  # This is a HUGE num seconds for now..final setting will be milliseconds
        healthy_forwarders = self.ACK_SCBD.get_components_for_timed_ack(timed_ack)

        num_healthy_forwarders = len(healthy_forwarders)
        if needed_workers > num_healthy_forwarders:
            result = self.insufficient_base_resources(input_params, healthy_forwarders)
            return result
        else:
            healthy_status = {"STATUS": "HEALTHY", "STATE":"READY_WITHOUT_PARAMS"}
            self.FWD_SCBD.set_forwarder_params(healthy_forwarders, healthy_status)

            ack_id = self.ncsa_resources_query(input_params, healthy_forwarders)

            self.ack_timer(3)

            #Check ACK scoreboard for response from NCSA
            ncsa_response = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
            if ncsa_response:
                pairs = {}
                ack_bool = None
                try:
                    ack_bool = ncsa_response[ACK_BOOL]
                    if ack_bool == True:
                        pairs = ncsa_response[PAIRS] 
                except KeyError, e:
                    pass 
                # Distribute job params and tell DMCS I'm ready.
                if ack_bool == TRUE:
                    fwd_ack_id = self.distribute_job_params(input_params, pairs)
                    self.ack_timer(3)

                    fwd_params_response = self.ACK_SCBD.get_components_for_timed_ack(fwd_ack_id)
                    if fwd_params_response and (len(fwd_params_response) == len(fwders)):
                        self.JOB_SCBD.set_value_for_job(job_num, "STATE", "BASE_TASK_PARAMS_SENT")
                        self.JOB_SCBD.set_value_for_job(job_num, "TIME_BASE_TASK_PARAMS_SENT", get_timestamp())
                        in_ready_state = {'STATE':'READY_WITH_PARAMS'}
                        self.FWD_SCBD.set_forwarder_params(fwders, in_ready_state) 
                        # Tell DMCS we are ready
                        result = self.accept_job(job_num)
                else:
                    #not enough ncsa resources to do job - Notify DMCS
                    idle_param = {'STATE': 'IDLE'}
                    self.FWD_SCBD.set_forwarder_params(healthy_forwarders, idle_params)
                    result = self.insufficient_ncsa_resources(ncsa_response)
                    return result

            else:
                result = self.ncsa_no_response(input_params)
                idle_param = {'STATE': 'IDLE'}
                self.FWD_SCBD.set_forwarder_params(forwarder_candidate_dict.keys(), idle_params)
                return result
                    

 
    def forwarder_health_check(self, params):
        job_num = str(params[JOB_NUM])
        raft_list = params['RAFTS']
        needed_workers = len(raft_list)

        self.JOB_SCBD.add_job(job_num, needed_workers)
        self.JOB_SCBD.set_value_for_job(job_num, "TIME_JOB_ADDED", get_timestamp())
        self.JOB_SCBD.set_value_for_job(job_num, "TIME_JOB_ADDED_E", get_epoch_timestamp())
        LOGGER.info('Received new job %s. Needed workers is %s', job_num, needed_workers)

        # run forwarder health check
        # get timed_ack_id
        timed_ack = self.get_next_timed_ack_id("FORWARDER_HEALTH_CHECK_ACK")

        forwarders = self.FWD_SCBD.return_available_forwarders_list()
        # Mark all healthy Forwarders Unknown
        state_status = {"STATE": "HEALTH_CHECK", "STATUS": "UNKNOWN"}
        self.FWD_SCBD.set_forwarder_params(forwarders, state_status)
        # send health check messages
        ack_params = {}
        ack_params[MSG_TYPE] = FORWARDER_HEALTH_CHECK
        ack_params["ACK_ID"] = timed_ack
        ack_params[JOB_NUM] = job_num
        
        self.JOB_SCBD.set_value_for_job(job_num, "STATE", "BASE_RESOURCE_QUERY")
        self.JOB_SCBD.set_value_for_job(job_num, "TIME_BASE_RESOURCE_QUERY", get_timestamp())
        audit_params = {}
        audit_params['DATA_TYPE'] = 'FOREMAN_ACK_REQUEST'
        audit_params['SUB_TYPE'] = 'FORWARDER_HEALTH_CHECK_ACK'
        audit_params['ACK_ID'] = timed_ack
        audit_parsms['COMPONENT_NAME'] = 'BASE_FOREMAN'
        audit_params['TIME'] = get_epoch_timestamp()
        for forwarder in forwarders:
            self._base_publisher.publish_message(self.FWD_SCBD.get_value_for_forwarder(forwarder,"CONSUME_QUEUE"),
                                            ack_params)

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


    def ncsa_resources_query(self, params, healthy_forwarders):
        job_num = str(params[JOB_NUM])
        raft_list = params[RAFTS]
        needed_workers = len(raft_list)
        LOGGER.info('Sufficient forwarders have been found. Checking NCSA')
        self._pairs_dict = {}
        forwarder_candidate_dict = {}
        for i in range (0, needed_workers):
            forwarder_candidate_dict[healthy_forwarders[i]] = raft_list[i]
            self.FWD_SCBD.set_forwarder_status(healthy_forwarders[i], NCSA_RESOURCES_QUERY)
            # Call this method for testing...
            # There should be a message sent to NCSA here asking for available resources
        timed_ack_id = self.get_next_timed_ack_id("NCSA_Ack") 
        ncsa_params = {}
        ncsa_params[MSG_TYPE] = "NCSA_RESOURCES_QUERY"
        ncsa_params[JOB_NUM] = job_num
        #ncsa_params[RAFT_NUM] = needed_workers
        ncsa_params[ACK_ID] = timed_ack_id
        ncsa_params["FORWARDERS"] = forwarder_candidate_dict
        self.JOB_SCBD.set_value_for_job(job_num, "STATE", "NCSA_RESOURCES_QUERY_SENT")
        self.JOB_SCBD.set_value_for_job(job_num, "TIME_NCSA_RESOURCES_QUERY_SENT", get_timestamp())
        self._ncsa_publisher.publish_message(self.NCSA_CONSUME, ncsa_params) 
        LOGGER.info('The following forwarders have been sent to NCSA for pairing:')
        LOGGER.info(forwarder_candidate_dict)
        return timed_ack_id


    def distribute_job_params(self, params, pairs):
        #ncsa has enough resources...
        job_num = str(params[JOB_NUM])
        self.JOB_SCBD.set_pairs_for_job(job_num, pairs)          
        self.JOB_SCBD.set_value_for_job(job_num, "TIME_PAIRS_ADDED", get_timestamp())
        LOGGER.info('The following pairs will be used for Job #%s: %s',
                     job_num, pairs)
        fwd_ack_id = self.get_next_timed_ack_id("FWD_PARAMS_ACK")
        fwders = pairs.keys()
        fwd_params = {}
        fwd_params[MSG_TYPE] = "FORWARDER_JOB_PARAMS"
        fwd_params[JOB_NUM] = job_num
        fwd_params[ACK_ID] = fwd_ack_id
        for fwder in fwders:
            fwd_params["TRANSFER_PARAMS"] = pairs[fwder]
            route_key = self.FWD_SCBD.get_value_for_forwarder(fwder, "CONSUME_QUEUE")
            self._base_publisher.publish_message(route_key, fwd_params)

        return fwd_ack_id


    def accept_job(self, job_num):
        dmcs_message = {}
        dmcs_message[JOB_NUM] = job_num
        dmcs_message[MSG_TYPE] = NEW_JOB_ACK
        dmcs_message[ACK_BOOL] = True
        self.JOB_SCBD.set_value_for_job(job_num, STATE, "JOB_ACCEPTED")
        self.JOB_SCBD.set_value_for_job(job_num, "TIME_JOB_ACCEPTED", get_timestamp())
        self._base_publisher.publish_message("dmcs_consume", dmcs_message)
        return True


    def insufficient_ncsa_resources(self, ncsa_response):
        dmcs_params = {}
        dmcs_params[MSG_TYPE] = "NEW_JOB_ACK"
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
        raft_list = params[RAFTS]
        needed_workers = len(raft_list)
        dmcs_params = {}
        dmcs_params[MSG_TYPE] = "NEW_JOB_ACK"
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
        distributors = [v['FQN'] for v in pairs.values()]
        forwarders = pairs.keys()

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
        

    def intake_yaml_file(self, filename):
        """This method reads the ForemanCfg.yaml config file
           found in the same directory as the BaseForeman class.
           The config file can list an initial set of forwarders and/or
           distributors, as well as the message broker address, default 
           file transfer values, etc.
    
        """
        try:
            f = open(filename)
        except IOError:
            print "Cant open %s" % filename
            print "Bailing out..."
            sys.exit(99)

        #cfg data map...
        cdm = yaml.safe_load(f)

        f.close()

        return cdm



    def get_next_timed_ack_id(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        retval = ack_type + "_" + str(self._next_timed_ack_id).zfill(6)
        return retval 


    def ack_timer(self, seconds):
        sleep(seconds)
        return True

    def purge_broker(self, queues):
        for q in queues:
            cmd = "rabbitmqctl -p /tester purge_queue " + q
            os.system(cmd)


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
