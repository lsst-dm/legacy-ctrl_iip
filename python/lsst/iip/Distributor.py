import pika
import yaml
import sys
import time
import logging
import os
import subprocess
import thread
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
        LOGGER.info('+++++++++++++------++++++++++++')
        LOGGER.info("Initializing Distributor object")
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
            print "Key error reading cfg file."
            print "Bailing out..."
            sys.exit(99)


        self._home_dir = "/home/" + self._name + "/"
        self._ncsa_broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._ncsa_broker_addr)

        self._msg_actions = { HEALTH_CHECK: self.process_foreman_check_health,
                              STANDBY: self.process_foreman_standby,
                              READOUT: self.process_foreman_readout }

        self.setup_publishers()
        self.setup_consumers()

    def setup_consumers(self):
        LOGGER.info('Distributor %s setting up consumer on %s', self._name, self._ncsa_broker_url)
        LOGGER.info('Starting new thread on consumer method')
        threadname = "thread-" + self._consume_queue

        self._consumer = Consumer(self._ncsa_broker_url, self._consume_queue)
        try:
            thread.start_new_thread(self.run_consumer, (threadname, 2,) )
            LOGGER.info('Started distributor consumer thread %s', threadname)
        except:
            LOGGER.critical('Cannot start Distributor consumer thread, exiting...')
            sys.exit(107)


    def run_consumer(self, threadname, delay):
        self._consumer.run(self.on_message)

    def setup_publishers(self):
        LOGGER.info('Setting up publisher for Distributor on %s', self._ncsa_broker_url)
        self._publisher = SimplePublisher(self._ncsa_broker_url)

    def on_message(self, ch, method, properties, body):
        msg_dict = yaml.load(body)
        LOGGER.info('In %s message callback', self._name)
        LOGGER.debug('Thread in %s callback is %s', self._name, thread.get_ident())
        LOGGER.debug('%s callback message body is: %s', self._name, str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


    def process_foreman_standby(self, params):
        """Right now, only three message types matter to Distributors:
           1) Health checks
           2) Standby, and
           3) Readout.
           This action method is for the standby message and asks the
           Distributor to clean up the target directory. Removing the
           Sentinel file is paramount, as leaving an old one in the
           target directory will have transfer time scripts thinking
           the transfer was instantaneous, or worse: it time travelled!

           :param dict params: the message body in python dict form.
           :rtype bool success/failure.
        """
        self._pairmate = params[MATE]
        self._job_num = params[JOB_NUM]
        LOGGER.info('Processing standby action for %s with the following setting: mate-%s ', self._name, self._pairmate)
        command = 'rm -f ' + self._target_dir + '*.test'
        result = subprocess.check_output(command, shell=True)
        msg_params = {}
        msg_params[MSG_TYPE] = 'DISTRIBUTOR_STDBY_ACK'
        msg_params['COMMENT1'] = "Result from running rm command: %s" % result
        self._publisher.publish_message('reports', yaml.dump(msg_params))

        standby_dict = {}
        standby_dict[MSG_TYPE] = "DISTRIBUTOR_STANDBY_ACK"
        standby_dict[JOB_NUM] = self._job_num
        standby_dict[NAME] = self._fqn_name
        standby_dict["ACK_BOOL"] = True
        standby_dict["TIMED_ACK"] = params["TIMED_ACK_ID"]
        self._publisher.publish_message(self._publish_queue, yaml.dump(standby_dict))


    def process_foreman_readout(self, params):
        LOGGER.info('At Top of Distributor readout')
        job_number = params[JOB_NUM]
        cmd = self._target_dir + "check_sentinel.sh"
        result = subprocess.check_output(cmd, shell=True)
        LOGGER.info('check_sentinel test is complete')
        # xfer complete
        #xfer_time = ""

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
        self._publisher.publish_message("reports", yaml.dump(msg))

        readout_dict = {}
        readout_dict[MSG_TYPE] = "DISTRIBUTOR_READOUT_ACK"
        readout_dict[JOB_NUM] = params[JOB_NUM]
        readout_dict[NAME] = self._fqn_name
        readout_dict["ACK_BOOL"] = True
        readout_dict["TIMED_ACK"] = params["TIMED_ACK_ID"]
        self._publisher.publish_message(self._publish_queue, yaml.dump(readout_dict))

    def process_foreman_check_health(self, params):
        Logger.info("Checking Distributor's health")
        # check health message
        msg = {}
        msg[MSG_TYPE] = "DISTRIBUTOR_HEALTH_ACK"
        msg[JOB_NUM] = params[JOB_NUM]
        msg[NAME] = self._fqn_name
        msg["ACK_BOOL"] = True
        msg["TIMED_ACK"] = params["TIMED_ACK_ID"]
        self._publisher.publish_message(self._publish_queue, yaml.dump(msg))


    def send_registration(self, msg_type):
        pass
        #acknowledge_msg = {'MSG_TYPE':'ack_' + msg_type,'MSG_NUM':str(Msg_num)}
        #Msg_num = Msg_num + 1
        #ack = yaml.dump(acknowledge_msg)

        #channel_to.queue_declare(queue=Qname_to)
        #channel_to.basic_publish(exchange='', routing_key=Qname_to, body=ack)



def main():
    logging.basicConfig(filename='logs/distributor.log', level=logging.INFO, format=LOG_FORMAT)
    dist = Distributor()
    print "Starting Distributor event loop..."
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print ""
    print "Distributor Finished"


if __name__ == "__main__": main()







