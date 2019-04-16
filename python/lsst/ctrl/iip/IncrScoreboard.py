# This file is part of ctrl_iip
# 
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from Scoreboard import Scoreboard
import redis
import sys
import yaml
import logging
from lsst.ctrl.iip.const import * 

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
  

    def __init__(self, db_type, db_instance, cred, cdm):
        super().__init__(cred, cdm)
        LOGGER.info('Setting up IncrScoreboard')
        self.DB_TYPE = db_type
        self.DB_INSTANCE = db_instance
        self._redis = self.connect()
        #Do NOT do this...in order to save sequence numbers between restarts
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
            return job
        else:
            LOGGER.error('Unable to increment job number due to lack of redis connection')

    def get_next_timed_ack_id(self, ack):
        if self.check_connection():
            self._redis.incr(self.ACK_SEQUENCE_NUM)
            ack_id = self._redis.get(self.ACK_SEQUENCE_NUM)
            id = str(ack) + "_" + str(ack_id).zfill(6)
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


    ##########################################
    ## These methods that add arbitrary values 
    ## to the sequence nums are for start up
    ## in case dump.rdb missed an increment
    ########################################### 

    def add_to_session_id(self, val):
        if self.check_connection():
            session_id = self._redis.get(self.SESSION_SEQUENCE_NUM)
            new_session_id = int(session_id) + val 
            self._redis.set(self.SESSION_SEQUENCE_NUM, new_session_id)
        else:
            LOGGER.error('Unable to add to session_id due to lack of redis connection')



    def add_to_job_num(self, val):
        if self.check_connection():
            job_num = self._redis.get(self.JOB_SEQUENCE_NUM)
            new_job_num = int(job_num) + val
            self._redis.set(self.JOB_SEQUENCE_NUM, new_job_num)
        else:
            LOGGER.error('Unable to add to job number due to lack of redis connection')


    def add_to_next_timed_ack_id(self, val):
        if self.check_connection():
            ack_id = self._redis.get(self.ACK_SEQUENCE_NUM)
            new_ack_id = int(ack_id) + val 
            self._redis.set(self.ACK_SEQUENCE_NUM, new_ack_id)
        else:
            LOGGER.error('Unable to add to ack_id due to lack of redis connection')



    def add_to_next_receipt_id(self, val):
        if self.check_connection():
            receipt_id = self._redis.get(self.RECEIPT_SEQUENCE_NUM)
            new_receipt_id = int(receipt_id) + val 
            self._redis.set(self.RECEIPT_SEQUENCE_NUM, new_receipt_id)
        else:
            LOGGER.error('Unable to add to receipt_id due to lack of redis connection')



    def print_all(self):
        all_forwarders = self.return_forwarders_list()
        for forwarder in all_forwarders:
            print(forwarder)
            print(self._redis.hgetall(forwarder))
        print("--------Finished In print_all--------")




