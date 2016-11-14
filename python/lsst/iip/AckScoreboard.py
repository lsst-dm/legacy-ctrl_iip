import redis
from toolsmod import get_timestamp
from toolsmod import get_epoch_timestamp
import yaml
import logging
from const import *
from Scoreboard import Scoreboard

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class AckScoreboard(Scoreboard):
    """Extends parent Scoreboard class and provides initialization
       for Redis ack table, each row being a new timed ack.

       As seen as in the first class variable below, when the 
       connection to Redis is opened, the Ack scoreboard is 
       assigned to Redis's Database instance 3. Redis launches with a default 
       15 separate database instances.
    """

    ### FIX: Put Redis DB numbers in Const
    TIMED_ACKS = 'timed_acks'
    TIMED_ACK_IDS = 'TIMED_ACK_IDS'
    ACK_FETCH = 'ACK_FETCH'
    ACKS_IDS = 'ACK_IDS'
  

    def __init__(self):
        """After connecting to the Redis database instance 
           ACK_SCOREBOARD_DB, this redis database is flushed 
           for a clean start. A 'charge_database' method is 
           included for testing the module.

           A new row will be added for each TIMED_ACK_ID. This will be
           done as follows:
           1) When a new TIMED_ACK_ID is encountered, row will be added with new ID as string identifier
           2) a list of hashes will be set up for each key/value pair in the message
           3) As new acks with a particular TIMED_ACK_ID are received, the data is added to that row.
           4) After a timer event elapses, the scoreboard is locked and checked  to see which ACKs were received.
        """
        LOGGER.info('Setting up AckScoreboard')
        try:
            Scoreboard.__init__(self, ACK_SCOREBOARD_DB)
        except L1RabbitConnectionError as e:
            LOGGER.error('Failed to make connection to Message Broker:  ', e.arg)
            print "No Auditing for YOU"
            raise L1Error('Calling super.init in AckScoreboard init caused: ', e.arg)

        self._redis = self.connect()
        self._redis.flushdb()
        #DEBUG_ONLY:
        #self.charge_database()
    

    def connect(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=ACK_SCOREBOARD_DB)
        return redis.Redis(connection_pool=pool) 


    def check_connection(self):
        ok_flag = False
        for i in range (1,4):
          try:
            response = self._redis.client_list()
            ok_flag = True
            break
          except redis.ConnectionError:
            self.connect()

        if ok_flag:
            if i == 1:
                return True
            else:
                LOGGER.info('In ACK Scoreboard, had to reconnect to Redis - all set now')
                return True
        else: 
            LOGGER.info('In ACK Scoreboard, could not reconnect to Redis after 3 attempts')
            return False



    def add_timed_ack(self, ack_msg_body):
        """The first time that a new ACK_ID is encountered, the ACK row is created.
           From then on, new ACKS for a particular ACK_ID are added here. 
            
           :param dict ack_msg_body: Description of an ACK enclosed within
               a system message 
        """

        ack_id_string = ack_msg_body['ACK_ID']
        ack_component_name = ack_msg_body['COMPONENT_NAME']
        ack_sub_type = ack_msg_body['MSG_TYPE']
      
        if self.check_connection():
            ack_msg_body['ACK_RETURN_TIME'] = get_timestamp()
            self._redis.hset(ack_id_string, ack_component_name, ack_msg_body)

            # ACK_IDS are for unit tests and for printing out entire scoreboard
            self._redis.lpush(self.ACK_IDS, ack_id_string)

            params = {}
            params['SUB_TYPE'] = ack_sub_type
            params['ACK_ID'] = ack_id_string
            params['COMPONENT_NAME'] = ack_component_name
            self.persist(self.build_audit_data(params))
            
        else:
            LOGGER.error('Unable to add new ACK; Redis connection unavailable')


    def get_components_for_timed_ack(self, timed_ack):
        """Return components who checked in successfully for a specific ack id.
           First check if row exists in scoreboard for timed_ack

           :param str timed_ack: The name of the ACK name to be checked.
           :rtype dict if row exists, otherwise
        """

        if self.check_connection():
            exists = self._redis.exists(timed_ack)
            if exists:
                component_dict = {}
                keys = self._redis.hkeys(timed_ack)
                for key in keys:
                   component_dict[key] = yaml.load(self._redis.hget(timed_ack, key))

                return component_dict
                params = {}
                params['SUB_TYPE'] = 'TIMED_ACK_FETCH'
                params['ACK_ID'] = timed_ack
                self.persist(self.build_audit_data(params))

            else:
                return None

    def build_audit_data(self, params):
        audit_data = {}
        keez = params.keys()
        for kee in keez:
            audit_data[kee] = params[kee]
        audit_data['TIME'] = get_epoch_timestamp()
        return audit_data



    def print_all(self):
        acks = self._redis.lrange(self.ACK_IDS, 0, -1)
        for ack in acks:
            x = self._redis.hgetall(ack)
            print x
            print ("---------")



def main():
    asb = AckScoreboard()

    asb.add_timed_ack(ncsa_msg)

    comps = asb.get_components_for_timed_ack('NCSA_16')


if __name__ == "__main__": main()
