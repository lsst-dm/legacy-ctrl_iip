import pika
from Scratchpad import Scratchpad
from toolsmod import get_timestamp
import yaml
import sys
import time
import logging
import os
import subprocess
import _thread
from const import *
from Consumer import Consumer
from SimplePublisher import SimplePublisher

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
             '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class Distributor:
    """This is a basic Distributor class. The cadence of the file
       is very similar to its workmate the Forwarder class and begins to
       viollate the DRY rule. It may be that this class and the
       Forwarder class are eventually combined into single class so that
       a personality can be chosen at the time of initialization. Or a
       parent class for both may be a better approach... but at this
       point, they are separate classes until it is certain that
       individual classes are definetely not necessary.
    """

    def __init__(self):
        LOGGER.info("Initializing Distributor object")
        self._registered = False
        f = open('DistributorCfg.yaml')

        # data map
        cdm = yaml.safe_load(f)
        try:
            self._name = cdm[NAME]
            self._passwd = cdm[PASSWD]
            self._fqn_name = cdm[FQN]
            self._ncsa_broker_addr = cdm[NCSA_BROKER_ADDR]
            self._consume_queue = cdm[CONSUME_QUEUE]
            self._publish_queue = cdm[PUBLISH_QUEUE]
            self._hostname = cdm[HOSTNAME]
            self._ip_addr = cdm[IP_ADDR]
            self._target_dir = cdm[TARGET_DIR]
            self._sentinel_file = cdm[SENTINEL_FILE]
        except KeyError as e:
            LOGGER.critical(e)
            print("Key error reading cfg file.")
            print("Bailing out...")
            sys.exit(99)


        self._home_dir = "/home/" + self._name + "/"
        self._ncsa_broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._ncsa_broker_addr)

        self._msg_actions = { DISTRIBUTOR_HEALTH_CHECK: self.process_health_check,
                              DISTRIBUTOR_JOB_PARAMS: self.process_job_params,
                              DISTRIBUTOR_READOUT: self.process_foreman_readout }

        self.setup_publishers()
        self.setup_consumers()
        self._job_scratchpad = Scratchpad(self._ncsa_broker_url)

    def setup_publishers(self):
        LOGGER.info('Setting up publisher for Distributor on %s', self._ncsa_broker_url)
        self._publisher = SimplePublisher(self._ncsa_broker_url)


    def setup_consumers(self):
        LOGGER.info('Distributor %s setting up consumer on %s', self._name, self._ncsa_broker_url)
        LOGGER.info('Starting new thread on consumer method')
        threadname = "thread-" + self._consume_queue

        self._consumer = Consumer(self._ncsa_broker_url, self._consume_queue)
        try:
            _thread.start_new_thread(self.run_consumer, (threadname, 2,) )
            LOGGER.info('Started distributor consumer thread %s', threadname)
        except:
            LOGGER.critical('Cannot start Distributor consumer thread, exiting...')
            sys.exit(107)


    def run_consumer(self, threadname, delay):
        self._consumer.run(self.on_message)

    def on_message(self, ch, method, properties, body):
        msg_dict = body
        print("GOT: %s", msg_dict)
        LOGGER.info('In %s message callback', self._name)
        LOGGER.debug('Thread in %s callback is %s', self._name, _thread.get_ident())
        LOGGER.debug('%s callback message body is: %s', self._name, str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


    def process_health_check(self, params):
        job_number = params[JOB_NUM]
        self._job_scratchpad.set_job_value(job_number, "STATE", "ADD_JOB")
        self._job_scratchpad.set_job_value(job_number, "ADD_JOB_TIME", get_timestamp())
        self.send_ack_response("DISTRIBUTOR_HEALTH_ACK", params)


    def process_job_params(self, params):
        job_number = params[JOB_NUM]
        transfer_params = params["TRANSFER_PARAMS"]
        self._job_scratchpad.set_job_transfer_params(params[JOB_NUM], transfer_params)
        self._job_scratchpad.set_job_value(job_number, "STATE", "READY_WITH_PARAMS")
        self._job_scratchpad.set_job_value(job_number, "READY_WITH_PARAMS_TIME", get_timestamp())
        self.send_ack_response(DISTRIBUTOR_JOB_PARAMS_ACK, params)


    def process_foreman_readout(self, params):
        LOGGER.info('At Top of Distributor readout')
        job_number = params[JOB_NUM]
        cmd = self._target_dir + "check_sentinel.sh"
        print("CMD: %s" % cmd)
        result = subprocess.check_output(cmd, shell=True)
        print("RESULT: %s" % result) 
        LOGGER.info('check_sentinel test is complete')
        # xfer complete
        #xfer_time = ""

###########XXXXXXXXXXXXXXX###############
####  Checking for and processing image file goes here
        command = "cat " + self._target_dir + "rcv_logg.test"
        cat_result = subprocess.check_output(command, shell=True)

        #filename = self._target_dir + "rcv_logg.test"
        #f = open(filename, 'r')
        #for line in f:
        #    xfer_time = xfer_time + line + "\n"
        msg = {}
        msg[MSG_TYPE] = 'XFER_TIME'
        msg[NAME] = self._name
        msg[JOB_NUM] = job_number
        msg['COMPONENT'] = "DISTRIBUTOR"
        msg['COMMENT1'] = "Result from xfer command is: %s" % result
        msg['COMMENT2'] = "cat_result is -->  %s" % cat_result
        msg['COMMENT3'] = "Command used to call check_sentinel.sh is %s" % cmd
        self._publisher.publish_message("reports", msg)

        readout_dict = {}
        readout_dict[MSG_TYPE] = "DISTRIBUTOR_READOUT_ACK"
        readout_dict[JOB_NUM] = params[JOB_NUM]
        readout_dict["COMPONENT_NAME"] = self._fqn_name
        readout_dict["ACK_BOOL"] = True
        readout_dict["ACK_ID"] = params["TIMED_ACK_ID"]
        print("PUBLISH_Q " % self._publish_queue)
        self._publisher.publish_message(self._publish_queue, readout_dict)

    def send_ack_response(self, type, params):
        print("PARAMS: %s" % params)
        timed_ack = params.get("ACK_ID")
        job_num = params.get(JOB_NUM)
        if timed_ack is None:
            LOGGER.info('%s failed, missing ACK_ID', type)
        elif job_num is None:
            LOGGER.info('%s failed, missing JOB_NUM for ACK ID: %s', type)
        else:
            msg_params = {}
            msg_params[MSG_TYPE] = type
            msg_params[JOB_NUM] = job_num
            msg_params["COMPONENT_NAME"] = self._fqn_name
            msg_params[ACK_BOOL] = "TRUE"
            msg_params[ACK_ID] = timed_ack
            self._publisher.publish_message(params["REPLY_QUEUE"], msg_params)
            print("ACK_ID: %s is sent." % timed_ack)
            LOGGER.info('%s sent for ACK ID: %s and JOB_NUM: %s', type, timed_ack, job_num)


    def register(self):
        pass
        #acknowledge_msg = {'MSG_TYPE':'ack_' + msg_type,'MSG_NUM':str(Msg_num)}
        #Msg_num = Msg_num + 1
        #ack = yaml.dump(acknowledge_msg)

        #channel_to.queue_declare(queue=Qname_to)
        #channel_to.basic_publish(exchange='', routing_key=Qname_to, body=ack)



def main():
    logging.basicConfig(filename='logs/distributor.log', level=logging.INFO, format=LOG_FORMAT)
    dist = Distributor()
    print("Starting Distributor event loop...")
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print("")
    print("Distributor Finished")


if __name__ == "__main__": main()
