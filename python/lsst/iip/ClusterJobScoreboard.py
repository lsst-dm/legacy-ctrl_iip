import redis
from toolsmod import get_timestamp
from toolsmod import get_epoch_timestamp
from toolsmod import L1RedisError
from toolsmod import L1RabbitConnectionError
import yaml
import logging
import time
import subprocess
from Scoreboard import Scoreboard
from const import *
import ClusterNodeScoreboard

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

'''
Structure:
           redis hash table
           key: job_num
           field: ccd_num
           value: dictionary
                  key: CCD_ID, CLUSTER_NODE, IP_ADDR, PATH_TO_FILE
'''

class ClusterJobScoreboard(Scoreboard):
    # CURRENT_SESSION_ID = 'CURRENT_SESSION_ID'
    VISIT_ROWS = 'visit_rows'
    # VISIT_HASH = 'visit_hash'
    DB_TYPE = ""
    DB_INSTANCE = None

    def __init__(self, db_type, db_instance):
        LOGGER.info('Setting up ClusterJobScoreboard')
        self.DB_TYPE = db_type
        self.DB_INSTANCE = db_instance
        self._session_id = str(1)
        try:
            Scoreboard.__init__(self)
        except L1RabbitConnectionError as e:
            LOGGER.error('Failed to make connection to Message Broker:  ', e.arg)
            print "No Monitoring for YOU"
            raise L1Error('Calling super.init in JobScoreboard init caused: ', e.arg)

        try:
            self._redis = self.connect()
        except L1RedisError as e:
            LOGGER.error("Cannot make connection to Redis:  " , e)
            print "No Redis for YOU"
            raise L1Error('Calling redis connect in JobScoreboard init caused:  ', e.arg)

        self._redis.flushdb()

        # self._redis.set(self.CURRENT_SESSION_ID, "session_100")

        LOGGER.info('JobScoreboard initialization is complete')

    
    def connect(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=self.DB_INSTANCE)
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
                LOGGER.info('In add_job, had to reconnect to Redis - all set now')
                return True
        else:
            LOGGER.info('In add_job, could not reconnect to Redis after 3 attempts')
            raise L1RedisError
            return False

    
    def assign_job_to_node(self, ccds, avail_node, job_num, dir_addr): # ccds: dict of ccd_num and distributers
                                                                     # avail_node: list of node
        if self.check_connection():
            count = 0
	    ret_dict = {}
            for ccd in ccds.keys():
                ccd_dict = {} # key: CCD_ID, CLUSTER_NODE, IP_ADDR, PATH_TO_FILE
                node = avail_node[count]

                # Setup dictionary
                ccd_dict['CLUSTER_NODE'] = node
                ccd_dict['CCD_ID'] = ccd
                ccd_dict['IP_ADDR'] = ccds[ccd] # distributor's ip address, maybe need change
                ccd_dict['PATH_TO_FILE'] = dir_addr + str(ccd)

                # Add the CCD dictionary to the redis hash, remember to yaml and unyaml
                self._redis.hset(job_num, ccd, yaml.dump(ccd_dict))
		ret_dict[node] = ccd_dict.copy()
                count += 1
	    return ret_dict
        else:
            LOGGER.error('Unable to add new job; Redis connection unavailable')

    
    def check_job_status(self, job_num, db): # return dictionary with ccd as key and tf as value
        ret = {}

        # Get the list of all value
        all_ccd_dict = self._redis.hgetall(job_num)
        for ccd_yaml in all_ccd_dict.values():
            # Load dictionary
            ccd_dict = yaml.load(ccd_yaml)
	    ccd_id = ccd_dict['CCD_ID']
            node = ccd_dict['CLUSTER_NODE']

            # Check if the job has finished
            ret[ccd_id] = True
            if db.get_node_state(node) != 'FINISHED':
                ret[ccd_id] = False
        
	return ret

    
    def store_visit_id(self, visit_id, bore_sight):
        self._redis.lpush(self.VISIT_ROWS, visit_id)
        self._redis.hset('visit_hash', visit_id, bore_sight)


def main():
  jbs = ClusterJobScoreboard()
  print "Cluster Job Scoreboard seems to be running OK"
  time.sleep(2)
  print "Done."

if __name__ == "__main__": main()
