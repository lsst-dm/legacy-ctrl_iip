## STATE Column: { STANDBY, PENDING_XFER, MAKING_XFER, XFER_COMPLETE }
## STATUS Column: { HEALTHY, UNHEALTHY, UNKNOWN }

import logging
import redis
import time
import sys
from Scoreboard import Scoreboard
from const import * 

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class DistributorScoreboard(Scoreboard):
    DISTRIBUTOR_ROWS = 'distributor_rows'
    ROUTING_KEY = 'ROUTING_KEY'
    PUBLISH_QUEUE = 'distributor_publish'

    def __init__(self, ddict):
        LOGGER.info('Setting up DistributorDcoreboard')
        self.connect()
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
        pool = redis.ConnectionPool(host='localhost', port=6379, db=DIST_SCOREBOARD_DB)
        self._redis = redis.Redis(connection_pool=pool)

    
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
        distributors = self._redis.lrange(self.DISTRIBUTOR_ROWS, 0, -1).decode("utf-8")
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
        return self._redis.hget(distributor, kee).decode("utf-8")


    def set_distributor_state(self, distributor, state):
        self._redis.hset(distributor,'STATE', state)
        #self.persist_snapshot(self._redis, "distributorscoreboard") 


    def set_distributor_status(self, distributor, status):
        self._redis.hset(distributor,'STATUS', status)
        #self.persist_snapshot(self._redis, "distributorscoreboard") 


    def get_routing_key(self, distributor):
        return self._redis.hget(distributor,'ROUTING_KEY').decode("utf-8")



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

