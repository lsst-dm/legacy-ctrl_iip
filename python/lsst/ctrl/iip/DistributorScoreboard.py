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


## STATE Column: { STANDBY, PENDING_XFER, MAKING_XFER, XFER_COMPLETE }
## STATUS Column: { HEALTHY, UNHEALTHY, UNKNOWN }

import logging
import redis
import time
import sys
from toolsmod import get_epoch_timestamp
from toolsmod import L1RedisError
from toolsmod import L1RabbitConnectionError
from Scoreboard import Scoreboard
from const import * 

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class DistributorScoreboard(Scoreboard):
    DISTRIBUTOR_ROWS = 'distributor_rows'
    ROUTING_KEY = 'ROUTING_KEY'
    PUBLISH_QUEUE = 'distributor_publish'
    DB_TYPE = ""
    DB_INSTANCE = None

    def __init__(self, db_type, db_instance, ddict):
        LOGGER.info('Setting up DistributorScoreboard')
        self.DB_TYPE = db_type
        self.DB_INSTANCE = db_instance

        try:
            Scoreboard.__init__(self)
        except L1RabbitConnectionError as e:
            LOGGER.error('Failed to make connection to Message Broker: %s', e.arg)
            print("No Monitoring for YOU")
            raise L1Error('Calling super.init in DistScoreboard init caused: %s', e.arg)

        try:
            self._redis = self.connect()
        except L1RedisError as e:
            LOGGER.error('Failed to make connection to Redis: %s', e.arg)
            print("No Redis for YOU")
            raise L1Error('Calling Redis connect in Distributor Scoreboard init caused: %s', e.arg)

        self._redis.flushdb()

        distributors = list(ddict.keys())
        for distributor in distributors:
            fields = ddict[distributor]
            name = fields['NAME']
            ip_addr = fields['IP_ADDR']
            target_dir = fields['TARGET_DIR']
            xfer_login = name + "@" + ip_addr 
            routing_key = fields['CONSUME_QUEUE']
            publish_queue = "distributor_publish"

            for field in fields:
                self._redis.hset(distributor, field, fields[field])
                self._redis.hset(distributor, 'XFER_LOGIN', xfer_login)
                self._redis.hset(distributor, 'STATUS', 'HEALTHY')
                self._redis.hset(distributor, 'ROUTING_KEY', routing_key)
                self._redis.hset(distributor, 'MATE', 'NONE')
  

            self._redis.lpush(self.DISTRIBUTOR_ROWS, distributor)
        
        #self.persist_snapshot(self._redis)


    def connect(self):
        #pool = redis.ConnectionPool(host='localhost', port=6379, db=self.DB_INSTANCE)
        #self._redis = redis.Redis(connection_pool=pool)
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

    
    def print_all(self):
        all_distributors = self.return_distributors_list()
        for distributor in all_distributors:
            print(distributor)
            print(self._redis.hgetall(distributor))
        print("--------Finished In get_all--------")
        #return self._redis.hgetall(all_distributors)


    def return_distributors_list(self):
        all_distributors = self._redis.lrange(self.DISTRIBUTOR_ROWS, 0, -1)
        return all_distributors


    def get_healthy_distributors_list(self): 
        healthy_distributors = []
        distributors = self._redis.lrange(self.DISTRIBUTOR_ROWS, 0, -1)
        for distributor in distributors:
            print("Checking health")
            if self._redis.hget(distributor, 'STATUS') == 'HEALTHY':
                print("Found a healthy distributor")
                healthy_distributors.append(distributor)

        return healthy_distributors


    def set_distributor_params(self, distributor, params):
        """The distributor paramater must be the fully
           qualified name, such as DISTRIBUTOR_2

        """
        for kee in list(params.keys()):
            self._redis.hset(distributor, kee, params[kee])
        #self.persist_snapshot(self._redis, "distributorscoreboard") 


    def set_value_for_multiple_distributors(self, distributors, kee, val):
        for distributor in distributors:
            self._redis.hset(distributor, kee, val)
        #self.persist_snapshot(self._redis, "distributorscoreboard") 


    def set_params_for_multiple_distributors(self, distributors, params):
        for distributor in distributors:
            kees = list(params.keys())
            for kee in kees:
                self._redis.hset(distributor, kee, params[kee])
        #self.persist_snapshot(self._redis, "distributorscoreboard") 


    def get_value_for_distributor(self, distributor, kee):
        return self._redis.hget(distributor, kee)


    def set_distributor_state(self, distributor, state):
        self._redis.hset(distributor,'STATE', state)
        #self.persist_snapshot(self._redis, "distributorscoreboard") 


    def set_distributor_status(self, distributor, status):
        self._redis.hset(distributor,'STATUS', status)
        #self.persist_snapshot(self._redis, "distributorscoreboard") 


    def get_routing_key(self, distributor):
        return self._redis.hget(distributor,'ROUTING_KEY')



def main():
    logging.basicConfig(filename='logs/DistributorScoreboard.log', level=logging.INFO, format=LOG_FORMAT)

    f = open('L1SystemCfg.yaml')

    #cfg data map...
    cdm = yaml.safe_load(f)
    ddict = cdm['ROOT']['XFER_COMPONENTS']['DISTRIBUTORS']

    dist = DistributorScoreboard(ddict)

    dist.print_all()

    """
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass
    """

    print("")
    print("DistributorScoreboard Done.")


if __name__ == "__main__": main()

