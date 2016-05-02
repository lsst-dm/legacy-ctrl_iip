import logging
import thread
import sys
import yaml
from Consumer import Consumer
from SimplePublisher import SimplePublisher

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

"""This file is a throwaway file used to temporarily
   generate messages as if it were the DMCS. The actual
   DMCS component with have policy built into it and
   handle aborts, catastrophies, and general 'job'
   bookkeeping. Again, this is just something to
   generate command messages.

"""

class DMCS_sim:
    DMCS_CONSUME = "dmcs_consume"

    def __init__(self):
        self._job_num = 0
        self._raft_num = 7
        self._options = self.get_options_string()
        self._broker_url = 'amqp://DMCS:DMCS@141.142.208.191:5672/%2fbunny'

        LOGGER.info('Setting up consumer on %s for %s', self._broker_url, self.DMCS_CONSUME)
        #self._connection = pika.BlockingConnection(pika.URLParameters('amqp://DMCS:DMCS@141.142.208.191:5672/%2fbunny'))
        self._dmcs_consumer = Consumer(self._broker_url, self.DMCS_CONSUME)
        try:
            thread.start_new_thread( self.run_dmcs_consumer, ("thread-dmce_consume", 2,) )
        except:
            LOGGER.error('Cannot start dmcs_consume thread')
            sys.exit(99)

        LOGGER.info('Setting up publisher on %s', self._broker_url)
        self._publisher = SimplePublisher(self._broker_url)



    def run_dmcs_consumer(self, threadname, delay):
        self._dmcs_consumer.run(self.on_dmcs_messages)


    def on_dmcs_messages(self, ch, method, properties, body):
        msg_dict = yaml.load(body)
        LOGGER.info('Latest message from Foreman: ')
        LOGGER.info('Message is %s', str(msg_dict))
        print msg_dict


    def run(self):
        while True:
            x = int(raw_input(self._options))
            if x == 1:
                pass
            elif x == 2:
                pass
            elif x == 3:
                pass
            elif x == 4:
                pass
            elif x == 5:  # Send Job msg
                self._job_num = self._job_num + 1
                params = {}
                params['MSG_TYPE'] = 'JOB'
                params['JOB_NUM'] = self._job_num
                params['RAFT_NUM'] = self._raft_num
                LOGGER.info('Sending JOB message %s', params)
                self._publisher.publish_message("dmcs_publish", yaml.dump(params))
            elif x == 6:  # Send Standby msg
                params = {}
                params['MSG_TYPE'] = 'STANDBY'
                params['JOB_NUM'] = self._job_num
                LOGGER.info('Sending STANDBY message %s', params)
                self._publisher.publish_message("dmcs_publish", yaml.dump(params))
            elif x == 7:  # Send Go msg
                params = {}
                params['MSG_TYPE'] = 'READOUT'
                params['JOB_NUM'] = self._job_num
                LOGGER.info('Sending READOUT message %s', params)
                self._publisher.publish_message("dmcs_publish", yaml.dump(params))
            elif x == 8:  # Send Abort msg
                pass

            elif x == 10: # set xfer file
                more_params = {}
                more_params['MSG_TYPE'] = 'SET_XFER_FILE'
                z = int(raw_input("    Choose xfer file: 1) 1k.test, 2) 193k.test, 3) 4meg.test, 4) 16.7meg.test, 5) 674meg.test... "))
                if z == 1:
                    more_params['XFER_FILE'] = '1k'
                    LOGGER.info('Sending xfer_file !k  message %s', params)
                    self._publisher.publish_message("dmcs_publish", yaml.dump(more_params))
                elif z == 2:
                    more_params['XFER_FILE'] = '193k'
                    LOGGER.info('Sending xfer_file !93k  message %s', params)
                    self._publisher.publish_message("dmcs_publish", yaml.dump(more_params))
                elif z == 3:
                    more_params['XFER_FILE'] = '4meg'
                    LOGGER.info('Sending xfer_file 4meg  message %s', params)
                    self._publisher.publish_message("dmcs_publish", yaml.dump(more_params))
                elif z == 4:
                    more_params['XFER_FILE'] = '16.7meg'
                    LOGGER.info('Sending xfer_file 16.7meg  message %s', params)
                    self._publisher.publish_message("dmcs_publish", yaml.dump(more_params))
                elif z == 5:
                    more_params['XFER_FILE'] = '674meg'
                    LOGGER.info('Sending xfer_file 674meg  message %s', params)
                    self._publisher.publish_message("dmcs_publish", yaml.dump(more_params))
                else:
                    pass
            elif x == 11: # set transfer file to
                pass
            elif x == 12:
                pass
            elif x == 13:
                pass
            elif x == 14:
                pass
            elif x == 20:
                params = {}
                params['MSG_TYPE'] = 'SET_XFER_APP'
                params['XFER_APP'] = 'ssh'
                LOGGER.info('Sending set_xfer_app SSH  message %s', params)
                self._publisher.publish_message("dmcs_publish", yaml.dump(params))
            elif x == 21:
                params = {}
                params['MSG_TYPE'] = 'SET_XFER_APP'
                params['XFER_APP'] = 'rsync'
                LOGGER.info('Sending set_xfer_app rsync  message %s', params)
                self._publisher.publish_message("dmcs_publish", yaml.dump(params))
            elif x == 22:
                params = {}
                params['MSG_TYPE'] = 'SET_XFER_APP'
                params['XFER_APP'] = 'ftp'
                LOGGER.info('Sending set_xfer_app ftp  message %s', params)
                self._publisher.publish_message("dmcs_publish", yaml.dump(params))
            elif x == 23:
                params = {}
                params['MSG_TYPE'] = 'SET_XFER_APP'
                params['XFER_APP'] = 'gridftp'
                LOGGER.info('Sending set_xfer_app gridftp  message %s', params)
                self._publisher.publish_message("dmcs_publish", yaml.dump(params))
            elif x == 24: # set raft number
                self._raft_num = int(raw_input('Enter integer number of rafts, 1 - 11 or less: '))
            else:
                pass


    def get_options_string(self):
        options = "\
        1 - Foreman Health Check,\n\
        2 - Forwarders Health Check,\n\
        3 - Distributors Health Check,\n\
        4 - \n\
        5 - Send Job,\n\
        6 - Send Standby,\n\
        7 - Send READOUT,\n\
        8 - Abort(Not yet implemented),\n\
        10 - Choose Xfer File,\n\
        20 - Set XFER App to SSH,\n\
        21 - Set XFER App to RSYNC,\n\
        22 - Set XFER App to FTP,\n\
        23 - Set XFER App to GridFTP,\n"

        return options



def main():
    logging.basicConfig(filename='logs/dmcs_sim.log', level=logging.INFO, format=LOG_FORMAT)
    dmcs = DMCS_sim()
    try:
        dmcs.run()
    except KeyboardInterrupt:
        pass

    print ""
    print "DMCS_sim Done."



if __name__ == "__main__": main()

#    try:
#      f = open('dmcs.conf')
#    except IOError:
#      logger.WARNING('Unable to open dmcs.conf')
#      logger.WARNING('Bailing out...')
#      sys.exit(99)
#
#    queues = f.readlines()
#    self.purge_queues(queues)
#
#  def purge_queues(self, queues):
#    for queue in queues:
#      queue_name = "name=" + str(queue)
#      call(['/usr/local/bin/rabbitmqadmin','-c', '/usr/local/bin/rabbitmqadmin.conf', '-V', 'bunny', 
#            '-u', 'DMCS', '-p', 'DMCS', 'purge', 'queue', queue_name])

