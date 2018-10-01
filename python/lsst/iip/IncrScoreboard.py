###############################################################################
###############################################################################
## Copyright 2000-2018 The Board of Trustees of the University of Illinois.
## All rights reserved.
##
## Developed by:
##
##   LSST Image Ingest and Distribution Team
##   National Center for Supercomputing Applications
##   University of Illinois
##   http://www.ncsa.illinois.edu/enabling/data/lsst
##
## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal with the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:
##
##   Redistributions of source code must retain the above copyright
##   notice, this list of conditions and the following disclaimers.
##
##   Redistributions in binary form must reproduce the above copyright
##   notice, this list of conditions and the following disclaimers in the
##   documentation and/or other materials provided with the distribution.
##
##   Neither the names of the National Center for Supercomputing
##   Applications, the University of Illinois, nor the names of its
##   contributors may be used to endorse or promote products derived from
##   this Software without specific prior written permission.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
## IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR
## ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
## CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
## WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE SOFTWARE.



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
    RECEIPT_SEQUENCE_NUM = 'RECEIPT_SEQUENCE_NUM' 
  

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
        if not (self._redis.exists(self.RECEIPT_SEQUENCE_NUM)):
            self._redis.set(self.RECEIPT_SEQUENCE_NUM, 100)
    


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
            print("In INCR scbd, next_job_num is %s" % job)
            return job
        else:
            LOGGER.error('Unable to increment job number due to lack of redis connection')

    def get_next_timed_ack_id(self, ack):
        if self.check_connection():
            self._redis.incr(self.ACK_SEQUENCE_NUM)
            ack_id = self._redis.get(self.ACK_SEQUENCE_NUM)
            id = str(ack) + "_" + str(ack_id).zfill(6)
            print("In INCR scbd, new ack_id is %s" % id)
            return id
        else:
            LOGGER.error('Unable to increment ACK_ID due to lack of redis connection')

    def get_next_receipt_id(self):
        if self.check_connection():
            self._redis.incr(self.RECEIPT_SEQUENCE_NUM)
            session_id = self._redis.get(self.RECEIPT_SEQUENCE_NUM)
            id = "Receipt_" + str(session_id)
            return id
        else:
            LOGGER.error('Unable to increment job number due to lack of redis connection')


    def print_all(self):
        all_forwarders = self.return_forwarders_list()
        for forwarder in all_forwarders:
            print(forwarder)
            print(self._redis.hgetall(forwarder))
        print("--------Finished In print_all--------")




