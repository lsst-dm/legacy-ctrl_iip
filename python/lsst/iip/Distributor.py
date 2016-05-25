import pika
import yaml
import sys
import time
import logging
import os
import subprocess
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
            self._broker_addr = cdm[BROKER_ADDR]
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
        self._broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._broker_addr)

        self._msg_actions = { CHECK_HEALTH: self.process_foreman_check_health,
                              STANDBY: self.process_foreman_standby,
                              READOUT: self.process_foreman_readout }

        self.setup_publishers()
        self.setup_consumers()

    def setup_consumers(self):
        LOGGER.info('Distributor %s setting up consumer on %s', self._name, self.broker_url)
        LOGGER.info('Starting new thread on consumer method')
        threadname = self._consume_queue

        self._consumer = Consumer(self._broker_url, self._consume_queue)
        try:
            thread.start_new_thread(self.run_consumer, (threadname, 2,) )
            LOGGER.info('Started distributor consumer thread %s', threadname)
        except e:
            Logger.critical('Cannot start Distributor consumer thread, exiting...')
            LOGGER.critical(e)
            sys.exit(107)


    def run_consumer(self, threadname, delay):
        self._consumer.run(self.on_message)

    def setup_publishers(self):
        LOGGER.info('Setting up publisher for Distributor on %s', self._broker_url)
        self._publisher = SimplePublisher(self._broker_url)

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
        command = 'rm ' + self._target_dir + '*.test'
        result = subprocess.check_output(command, shell=True)
        msg_params = {}
        msg_params[MSG_TYPE] = 'DISTRIBUTOR_STDBY_ACK'
        msg_params['COMMENT1'] = "Result from running rm command: %s" % result
        self._publisher.publish_message('reports', yaml.dump(msg_params))


    def process_foreman_readout(self, params):
        job_number = params[JOB_NUM]
        command = self._target_dir + "check_sentinel.sh"
        result = subprocess.check_output(command, shell=Trus)
        # xfer complete
        xfer_time = ""
        filename = self._target_dir + "rcv_logg"
        f = open(filename, 'r')
        for line in f:
            xfer_time = xfer_time + line + "\n"
        msg = {}
        msg[MSG_TYPE] = 'XFER_TIME'
        msg[NAME] = self._name
        msg[JOB_NUM] = job_number
        msg['FINISH_TIME'] = xfer_time
        msg['COMMENT1'] = "Result from xfer command is: %s" % result
        self._publisher.publish_message("reports", yaml.dump(msg))


    def process_foreman_check_health(self, params):
        pass # for now...



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







