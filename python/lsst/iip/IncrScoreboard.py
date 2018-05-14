from Scoreboard import Scoreboard
import redis
import sys
import yaml
import logging
from const import * 

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class IncrScoreboard(Scoreboard):
    FORWARDER_ROWS = 'forwarder_rows'
    PUBLISH_QUEUE = 'forwarder_publish'
    DB_TYPE = ""
    DB_INSTANCE = None
    SESSION_SEQUENCE_NUM = 'SESSION_SEQUENCE_NUM' 
    JOB_SEQUENCE_NUM = 'JOB_SEQUENCE_NUM' 
    ACK_SEQUENCE_NUM = 'ACK_SEQUENCE_NUM' 
  

    def __init__(self, db_type, db_instance):
        LOGGER.info('Setting up IncrScoreboard')
        self.DB_TYPE = db_type
        self.DB_INSTANCE = db_instance
        self._redis = self.connect()
        #Do NOT do this...
        #self._redis.flushdb()

        # FIX Test that incrementable vals already exist - else set them to 100, or some such...
        if not (self._redis.exists(self.SESSION_SEQUENCE_NUM)):
            self._redis.set(self.SESSION_SEQUENCE_NUM, 100)
        if not (self._redis.exists(self.JOB_SEQUENCE_NUM)):
            self._redis.set(self.JOB_SEQUENCE_NUM, 1000)
        if not (self._redis.exists(self.ACK_SEQUENCE_NUM)):
            self._redis.set(self.ACK_SEQUENCE_NUM, 1)
    


    def connect(self):
        #pool = redis.ConnectionPool(host='localhost', port=6379, db=self.DB_INSTANCE)
        #return redis.Redis(connection_pool=pool)
        try:
            sconn = redis.StrictRedis(host='localhost',port='6379', \
                                      charset='utf-8', db=self.DB_INSTANCE, \
                                      decode_responses=True)
            sconn.ping()
            LOGGER.info("Redis connected. Connection details are: %s", sconn)
            return sconn
        except Exception as e:
            LOGGER.critical("Redis connection error: %s", e)
            LOGGER.critical("Exiting due to Redis connection failure.")
            sys.exit(100)


    def check_connection(self):
        ok_flag = False
        for i in range (1,4):
            try:
                #response = self._redis.client_list()
                response = self._redis.ping()
                ok_flag = True
                break
            except redis.ConnectionError:
                self.connect()

        if ok_flag:
            if i == 1:
                return True
            else:
                LOGGER.info('In add_job, had to reconnect to Redis - all set now')
                return True
        else:
            LOGGER.info('In add_job, could not reconnect to Redis after 3 attempts')
            raise L1RedisError
            return False


    def get_next_session_id(self):
        if self.check_connection():
            self._redis.incr(self.SESSION_SEQUENCE_NUM)
            session_id = self._redis.get(self.SESSION_SEQUENCE_NUM)
            id = "Session_" + str(session_id)
            return id
        else:
            LOGGER.error('Unable to increment job number due to lack of redis connection')

    def get_next_job_num(self, session):
        if self.check_connection():
            self._redis.incr(self.JOB_SEQUENCE_NUM)
            job_num = self._redis.get(self.JOB_SEQUENCE_NUM)
            job = str(session) + "_" + str(job_num)
            return job
        else:
            LOGGER.error('Unable to increment job number due to lack of redis connection')

    def get_next_timed_ack_id(self, type):
        if self.check_connection():
            self._redis.incr(self.ACK_SEQUENCE_NUM)
            ack_id = self._redis.get(self.ACK_SEQUENCE_NUM)
            id = str(type) + "_" + str(ack_id).zfill(6)
            return id
        else:
            LOGGER.error('Unable to increment ACK_ID due to lack of redis connection')


    def print_all(self):
        all_forwarders = self.return_forwarders_list()
        for forwarder in all_forwarders:
            print(forwarder)
            print(self._redis.hgetall(forwarder))
        print("--------Finished In print_all--------")




