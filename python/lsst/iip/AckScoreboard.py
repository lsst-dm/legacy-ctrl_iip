import redis
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
    ACK_SCOREBOARD_DB = 3
    TIMED_ACKS = 'timed_acks'
    TIMED_ACK_ID = 'TIMED_ACK_ID'
  

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
        self._redis = self.connect()
        self._redis.flushdb()
        #DEBUG_ONLY:
        #self.charge_database()
    

    def connect(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=self.ACK_SCOREBOARD_DB)
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
        """The first time that a new TIMED_ACK_ID is encountered, the ACK row is created.
           From then on, new ACKS for a particulat ACK_ID are added here. 
            
           :param yaml'd text ack_msg_body: Description of an ACK enclosed within
               a system message that has been sertialized with yaml  
        """
        ack_id_string = ack_msg_body[TIMED_ACK]
      
        if self.check_connection():
            self._redis.hset(ack_id_string, ack_msg_body[COMPONENT_NAME], ack_msg_body[ACK_BOOL])

            # This next line builds a list of TIMED_ACK_IDs for use in unit tests and as a general 
            # component for printing out the entire scoreboard
            self._redis.lpush(self.ACKS, ack_id_string)
            #self.persist_snapshot()
        else:
            LOGGER.error('Unable to add new ACK; Redis connection unavailable')


    def get_components_for_timed_ack(self, timed_ack):
        """Return components who checked in successfully for a specific job number.

           :param str timed_ack: The name of the ACK name to be checked.
           :rtype dict
        """
        if self.check_connection():
            component_dict = {}
            keys = self._redis.hkeys(timed_ack)
            for key in keys:
                component_dict[key] = hget(timed_ack, key)

        return component_dict


    def print_all(self):
        acks = self._redis.lrange(self.ACKS, 0, -1)
        for ack in acks:
            x = self._redis.hgetall(ack)
            print x


    def charge_database(self):

        pass


def main():
    asb = AckScoreboard()


if __name__ == "__main__": main()
