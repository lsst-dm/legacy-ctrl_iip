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

class Forwarder:
    """Presents a vanilla L1 Forwarder personality. In
       nightly operation, at least 21 of these 
       components will be available at any time (one for each raft).
    """

    def __init__(self):
        LOGGER.info('+++++++++++++------++++++++++++')
        LOGGER.info("Initializing Forwarder")
        self._registered = False
        f = open('ForwarderCfg.yaml')
        #cfg data map...
        cdm = yaml.safe_load(f)
        try:
            self._name = cdm[NAME]
            self._passwd = cdm[PASSWD]
            self._fqn_name = cdm[FQN]
            self._broker_addr = cdm[BROKER_ADDR]
            self._consume_queue = cdm[CONSUME_QUEUE]
            self._publish_queue = cdm[PUBLISH_QUEUE]
            self._xfer_app = cdm[XFER_APP]
            self._xfer_file = cdm[XFER_FILE]
            self._hostname = cdm[HOSTNAME]
            self._ip_addr = cdm[IP_ADDR]
        except KeyError as e:
            LOGGER.critical(e)
            print "Missing base keywords in yaml file... Bailing out..."
            sys.exit(99)

        self._home_dir = "/home/" + self._name + "/"
        self._broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._broker_addr)

        self._msg_actions = { CHECK_HEALTH: self.process_foreman_check_health,
                              STANDBY: self.process_foreman_standby,
                              SET_XFER_APP: self.process_foreman_set_xfer_app,
                              SET_XFER_FILE: self.process_foreman_set_xfer_file,
                              READOUT: self.process_foreman_readout }

        self.setup_publishers()
        self.setup_consumers()

 
    def setup_consumers(self):
        LOGGER.info('Setting up consumers on %s', self._broker_url)
        LOGGER.info('Running start_new_thread on all consumer methods')
        threadname = "thread-" + self._consume_queue
        print "Threadname is %s" % threadname

        self._consumer = Consumer(self._broker_url, self._consume_queue)
        try:
            thread.start_new_thread( self.run_consumer, (threadname, 2,) )
            LOGGER.info('Started forwarder consumer thread %s', threadname)
            print "Started Consumer Thread"
        except:
            LOGGER.critical('Cannot start forwarder consumer thread, exiting...')
            sys.exit(99)


    def run_consumer(self, threadname, delay):
        self._consumer.run(self.on_message)


    def setup_publishers(self):
        LOGGER.info('Setting up publisher on %s', self._broker_url)
        self._publisher = SimplePublisher(self._broker_url)


    def on_message(self, ch, method, properties, body):
        msg_dict = yaml.load(body)
        LOGGER.info('In %s  message callback', self._name)
        LOGGER.debug('Thread in %s callback is %s', self._name, thread.get_ident())
        LOGGER.debug('%s callback message body is: %s', self._name, str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


    def process_foreman_standby(self, params):
        self._pairmate = params[MATE]
        self._xfer_login = params[XFER_LOGIN]
        self._xfer_app = params[XFER_APP]
        self._xfer_file = params[XFER_FILE]
        LOGGER.info('Processing standby action for %s with the following settings: mate-%s   xfer_login-%s   xfer_app-%s   xfer_file-%s', self._name, self._pairmate, self._xfer_login, self._xfer_app, self._xfer_file)
        msg_params = {}
        msg_params[MSG_TYPE] = 'FORWARDER_STDBY_ACK'
        self._publisher.publish_message("reports", yaml.dump(msg_params))


    def process_foreman_readout(self, params):
        """There are two approaches for this method below.
           The first calls a shell script outside the Forwarder
           process in order to xfer the file.
          
           The second approach implements the timing actions for the call within
           the Forwarder process, and calls scp directly. The second approach is 
           written so that the timing results can be easily published as a message.

           Two files are transferred each time READOUT is called...the actual data file,
           and a small sentinel file. Instead of scp'ing each file, the directory where these two
           files reside is used as the 'transfer file' and is moved with the recursive
           '-r' switch.

        """

        job_number = params[JOB_NUM]
        #source_dir = self._home_dir + self._xfer_file
        source_dir = self._home_dir + "xfer_dir"
        
        datetime1 = subprocess.check_output('date +"%Y-%m-%d %H:%M:%S.%5N"', shell=True)

        # Still one conection for both files, but files are sent to scp in proper xfer order
        #FIX ':xfer_dir' must be changed to a mutable target dir...
        cmd = 'cd ~/xfer_dir && scp -r $(ls -t)' + ' ' + str(self._xfer_login) + ':xfer_dir'

        #remove datetime line below for production
        datetime2 = subprocess.check_output('date +"%Y-%m-%d %H:%M:%S.%5N"', shell=True)
        proc = subprocess.check_output(cmd, shell=True)
        LOGGER.info('%s readout message action; command run in os at %s is: %s ',self._name, datetime1, cmd)
        LOGGER.info('File xfer command completed (returned) at %s', datetime2)
        msg_params = {}
        msg_params['COMMENT1'] = "File Transfer Time start time: %s" % datetime1
        msg_params['COMMENT2'] = "Result from start xfer command is %s" % proc
        msg_params[MSG_TYPE] = 'XFER_COMPLETE'
        msg_params['COMPONENT'] = 'FORWARDER'
        msg_params['JOB_NUM'] = params[JOB_NUM]
        msg_params[NAME] = self._name
        msg_params['EVENT_TIME'] = "Transfer completion time = %s" % datetime2
        msg_params['SOURCE_DIR'] = source_dir
        msg_params['COMMAND'] = cmd
        self._publisher.publish_message('reports', yaml.dump(msg_params))


    def process_foreman_set_xfer_app(self, params):
        self._xfer_app = params[self.XFER_APP]
        LOGGER.info('Setting transfer App for %s to %s', self._name, self._xfer_app)


    def process_foreman_set_xfer_file(self, params):
        self._xfer_file = params[self.XFER_FILE]
        LOGGER.info('Setting transfer file for %s to %s', self._name, self._xfer_file)


    def process_foreman_check_health(self, params):
        pass # for now... 

    def register(self):
        pass
        # pass in msg to foreman stating cfg settings
        # pass in name of special one time use queue that will be deleted afterwards
        # Returm message will have a possible delta...
        # If return NAME is different, consume queue will need to be changed
        # and self._home_dir will need repairing, possibly more.



def main():
    logging.basicConfig(filename='logs/forwarder.log', level=logging.INFO, format=LOG_FORMAT)
    fwd = Forwarder()
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print ""
    print "Forwarder Finished"


if __name__ == "__main__": main()
