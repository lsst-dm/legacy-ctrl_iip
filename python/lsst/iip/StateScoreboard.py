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

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class StateScoreboard(Scoreboard):
    JOBS = 'JOBS'
    SESSIONS = 'SESSIONS'
    VISITS = 'VISITS'
    JOB_NUM = 'JOB_NUM'
    WORKER_NUM = 'worker_num'
    STATE = 'STATE'
    JOB_STATUS = 'JOB_STATUS'
    STATUS = 'STATUS'
    SUB_TYPE = 'SUB_TYPE'
    JOB_SEQUENCE_NUM = 'JOB_SEQUENCE_NUM'
    SESSION_SEQUENCE_NUM = 'SESSION_SEQUENCE_NUM'
    DB_INSTANCE = None
    AR = "archive"
    PP = "prompt_process"
    CU = "catchup_archive"
  

    def __init__(self, db_instance):
        self.DB_INSTANCE = db_instance
        self._session_id = str(1)
        try:
            Scoreboard.__init__(self)
        except L1RabbitConnectionError as e:
            LOGGER.error('Failed to make connection to Message Broker:  ', e.arg)
            print "No Monitoring for YOU"
            raise L1Error('Calling super.init in StateScoreboard init caused: ', e.arg)

        try:
            self._redis = self.connect()
        except L1RedisError as e:
            LOGGER.error("Cannot make connection to Redis:  " , e)  
            print "No Redis for YOU"
            raise L1Error('Calling redis connect in StateScoreboard init caused:  ', e.arg)

        self._redis.flushdb()

        weekday = subprocess.check_output('date +"%u"', shell=True)
        job_num_seed = str(weekday) + "000"
        #set up auto sequence
        self._redis.set(self.JOB_SEQUENCE_NUM, int(job_num_seed))
        self._redis.set(self.SESSION_SEQUENCE_NUM, 1000)
      
    

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


    def set_archive_state(self, state):
        if self.check_connection():
            self._redis.hset(self.AR, STATE, state)

    def get_archive_state(self):
        if self.check_connection():
            return self._redis.hget(self.AR, STATE)


    def set_prompt_process_state(self, state):
        if self.check_connection():
            self._redis.hset(self.PP, STATE, state)

    def get_prompt_process_state(self):
        if self.check_connection():
            return self._redis.hget(self.PP, STATE)


    def set_catchup_archive_state(self, state):
        if self.check_connection():
            self._redis.hset(self.CU, STATE, state)

    def get_catchup_archive_state(self):
        if self.check_connection():
            return self._redis.hget(self.CU, STATE)







    def get_value_for_job(self, job_number, kee):
        """Return a value for a specific field.
  
           :param str job_number: The job in which field value is needed.
           :param str kee: The name of the field to retrieve desired data.
        """
        if self.check_connection():
            return self._redis.hget(str(job_number), kee)
        else:
            return None


    def set_pairs_for_job(self, job_number, pairs):
        """Pairs is a temporary relationship between Forwarders 
           and Distributors that lasts for one job. Note the use of yaml...
           Unlike python dicts, Redis is not a nested level database. For a 
           field to have a dict attached to it, it is necessary to serialize 
           the dict using yaml, json, or pickle. Pyyaml is already in use 
           for conf files.

           :param str job_number: cast as str below just to make certain.
           :param  dict pairs: Forwarders and Distributors arranged in a
           dictionary.
        """
        if self.check_connection():
            self._redis.hset(str(job_number), 'PAIRS', yaml.dump(pairs))
            return True
        else:
            return False


    def get_pairs_for_job(self, job_number):
        """Return Forwarder-Distributor pairs for a specific job number.

           :param str job_number: The job associated with the pairs.
           :rtype dict
        """
        if self.check_connection():
            pairs =  self._redis.hget(str(job_number), 'PAIRS')
        ### XXX FIX - Check for existence of pairs...
        if pairs:
            return yaml.load(pairs)
        else:
            return None

    def set_ccds_for_job(self, job_number, ccds):
        """Pairs is a temporary relationship between Forwarders 
           and Distributors that lasts for one job. Note the use of yaml...
           Unlike python dicts, Redis is not a nested level database. For a 
           field to have a dict attached to it, it is necessary to serialize 
           the dict using yaml, json, or pickle. Pyyaml is already in use 
           for conf files.

           :param str job_number: cast as str below just to make certain.
           :param  dict pairs: Forwarders and Distributors arranged in a
           dictionary.
        """
        if self.check_connection():
            self._redis.hset(str(job_number), 'CCDS', yaml.dump(ccds))
            return True
        else:
            return False


    def get_ccds_for_job(self, job_number):
        if self.check_connection():
            ccds =  self._redis.hget(str(job_number), 'CCDS')
        ### XXX FIX - Check for existence of pairs...
        if ccds:
            return yaml.load(ccds)
        else:
            return None


    def delete_job(self, job_number):
        #self._redis.hdel(self.JOBS, str(job_number))
        self._redis.lrem(self.JOBS, 0, str(job_number))


    def build_monitor_data(self, params):
        monitor_data = {}
        keez = params.keys()
        for kee in keez:
            monitor_data[kee] = params[kee]
        monitor_data['SESSION_ID'] = self.get_current_session()
        monitor_data['VISIT_ID'] = self.get_current_visit()
        monitor_data['TIME'] = get_epoch_timestamp()
        monitor_data['DATA_TYPE'] = self.DBTYPE
        return monitor_data


    def get_next_session_(self, device):
        if self.check_connection():
            self._redis.incr(self.SESSION_SEQUENCE_NUM)
            session_id = self._redis.hget(self.SESSION_SEQUENCE_NUM)
            if device == "AR":
                self._redis.hset(self.AR, 'SESSION_ID', session_id)
            if device == "PP":
                self._redis.hset(self.PP, 'SESSION_ID', session_id)
            if device == "CU":
                self._redis.hset(self.CU, 'SESSION_ID', session_id)
            return session_id
        else:
            LOGGER.error('Unable to increment job number due to lack of redis connection')
            #RAISE exception to catch in DMCS.py


    def get_current_session_id(self):
        if self.check_connection():
            return self._redis.hget(self.SESSION_SEQUENCE_NUM)
        else:
            LOGGER.error('Unable to increment job number due to lack of redis connection')
            #RAISE exception to catch in DMCS.py


    def get_next_job_num(self, prefix):
        if self.check_connection():
            self._redis.incr(self.JOB_SEQUENCE_NUM)
            job_num_str = prefix + str( self._redis.hget(self.JOB_SEQUENCE_NUM))
            return job_num_str
        else:
            LOGGER.error('Unable to increment job number due to lack of redis connection')
            #RAISE exception to catch in DMCS.py



    def print_all(self):
        dump_dict = {}
        f = open("dump", 'w')
        jobs = self._redis.lrange(self.JOBS, 0, -1)
        for job in jobs:
            x = self._redis.hgetall(job)
            dump_dict[job] = x

        f.write(yaml.dump(dump_dict))
        print dump_dict


def main():
  jbs = JobScoreboard()
  print "Job Scoreboard seems to be running OK"
  time.sleep(2)
  print "Done."
  #jbs.charge_database()
  #jbs.print_all()
  #Ps = jbs.get_value_for_job(str(1), 'PAIRS')
  #print "printing Ps"
  #print Ps
  #ppps = eval(Ps)
  #pps = ppps.keys()
  #print "final line"
  #print ppps == pairs



if __name__ == "__main__": main()
