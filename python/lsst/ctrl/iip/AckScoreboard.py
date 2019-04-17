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


import redis
from lsst.ctrl.iip.toolsmod import get_timestamp
from lsst.ctrl.iip.toolsmod import get_epoch_timestamp
from lsst.ctrl.iip.toolsmod import L1RedisError
from lsst.ctrl.iip.toolsmod import L1RabbitConnectionError
import yaml
import copy
import datetime
import logging
from time import sleep
from lsst.ctrl.iip.const import *
from lsst.ctrl.iip.Scoreboard import Scoreboard

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
    ACK_IDS = 'ACK_IDS'
    DB_TYPE = ""
    DB_INSTANCE = None
  

    def __init__(self, db_type, db_instance, cred, cdm):
        """After connecting to the Redis database instance 
           ACK_SCOREBOARD_DB, this redis database is flushed 
           for a clean start. 

           A new row will be added for each TIMED_ACK_ID. This will be
           done as follows:
           1) When a new TIMED_ACK_ID is encountered, row will be added with new ID as string identifier
           2) a list of hashes will be set up for each key/value pair in the message
           3) As new acks with a particular TIMED_ACK_ID are received, the data is added to that row.
           4) After a timer event elapses, the scoreboard is locked and checked  to see which ACKs were received.
        """
        super().__init__(cred, cdm)
        LOGGER.info('Setting up AckScoreboard')
        self.DB_TYPE = db_type
        self.DB_INSTANCE = db_instance

        self._redis = self.connect()
        self._redis.flushdb()
        #DEBUG_ONLY:
        #self.charge_database()
    

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
        ack_component_name = ack_msg_body['COMPONENT']
        ack_sub_type = ack_msg_body['MSG_TYPE']
      
        if self.check_connection():
            self._redis.hset(ack_id_string, ack_component_name, yaml.dump(ack_msg_body))
        #    l = []
        #    if self._redis.hget(ack_id_string, 'COMPONENTS') == None:
        #        # Make the list structure and add component name to list and yaml
        #        l.append(ack_component_name)
        #        self._redis.hset(ack_id_string, 'COMPONENTS', yaml.dump(l))
        #    else:
        #        # un yaml list, and component name, then re - yaml
        #        l = yaml.safe_load(self._redis.hget(ack_id_string, 'COMPONENTS'))
        #        l.append(ack_component_name)
        #        self._redis.hset(ack_id_string, 'COMPONENTS', yaml.dump(l))

            # ACK_IDS are for unit tests and for printing out entire scoreboard
            #self._redis.lpush(self.ACK_IDS, ack_id_string)
            
       #     params = {}
       #     params['SUB_TYPE'] = ack_sub_type
       #     params['ACK_ID'] = ack_id_string
       #     if 'JOB_NUM' in ack_msg_body:
       #         params['JOB_NUM'] = ack_msg_body['JOB_NUM']
       #     if 'IMAGE_ID' in ack_msg_body:
       #         params['IMAGE_ID'] = ack_msg_body['IMAGE_ID']
       #     params['COMPONENT'] = ack_component_name
       #     params['ACK_BOOL'] = ack_msg_body['ACK_BOOL']
       #     self.persist(self.build_audit_data(params))
            
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
                   component_dict[key] = yaml.safe_load(self._redis.hget(timed_ack, key))

                return component_dict
                
                params = {}
                params['SUB_TYPE'] = 'TIMED_ACK_FETCH'
                params['ACK_ID'] = timed_ack
                self.persist(self.build_audit_data(params))
                
            else:
                return None


    def add_pending_nonblock_ack(self, params):
        ack_id_string = params['ACK_ID']
        if self.check_connection():
            self._redis.hset('PENDING_ACKS', ack_id_string, params['EXPIRY_TIME'])


    def resolve_pending_nonblock_acks(self):
        # For ack_ids in pending acks,
        #     check for ack by calling get_timed_ack with ack_id
        #     If there, grab it and remove entry from pending acks with HDEL
        #         If more than one component, there is a problem - pending acks are all unique components and IDs
        #     If not there and EXPIRY time exceeded, raise 'no ack' alarm 
        if self._redis.exists('PENDING_ACKS'):
            keez = self._redis.hkeys('PENDING_ACKS')
            for kee in keez:
                if self._redis.exists(kee): # ack is here - don't check time
                    self._redis.hdel('PENDING_ACKS', kee) # Remove so we don't check again
                else:
                    expiry = self._redis.hget('PENDING_ACKS', kee)
                    now = datetime.datetime.now().time()
                    if now > expiry:  # if timeout is expired...else do nothing and check next time
                        self._redis.lpush('MISSING_NONBLOCK_ACKS', kee) # handled by self.check_missing_acks()
                        self._redis.hdel('PENDING_ACKS', kee)



    def check_missing_acks(self):
        pass


    def build_audit_data(self, params):
        audit_data = {}
        keez = list(params.keys())
        for kee in keez:
            audit_data[kee] = params[kee]
        audit_data['TIME'] = get_epoch_timestamp()
        audit_data['DATA_TYPE'] = self.DB_TYPE
        return audit_data



    def print_all(self):
        acks = self._redis.lrange(self.ACK_IDS, 0, -1)
        for ack in acks:
            x = self._redis.hgetall(ack)
            print(x)
            print ("---------")



def main():
    asb = AckScoreboard("Test", 3)
    print("AckScoreboard seems to be running OK.")


if __name__ == "__main__": main()
