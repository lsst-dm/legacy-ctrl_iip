import redis
import yaml
import logging
import subprocess
from Scoreboard import Scoreboard

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class JobScoreboard(Scoreboard):
    """Extends parent Scoreboard class and provides initialization
       for Redis jobs table, each row being a new job.

       As seen as in the first class variable below, when the 
       connection to Redis is opened, the Job scoreboard is 
       assigned to Redis's rdDatabase instance 8. Redis launches with a default 
       15 separate database instances.
    """
    JOB_SCOREBOARD_DB = 8
    JOBS = 'jobs'
    JOB_NUM = 'JOB_NUM'
    WORKER_NUM = 'worker_num'
    RAFTS = 'RAFTS'
    STATE = 'STATE'
    XFER_APP = 'XFER_APP'
    XFER_FILE = 'XFER_FILE'
    JOB_SEQUENCE_NUM = 'JOB_SEQUENCE_NUM'
  

    def __init__(self):
        """After connecting to the Redis database instance 
           JOB_SCOREBOARD_DB, this redis database is flushed 
           for a clean start. A 'charge_database' method is 
           included for testing the module.

           Each job will be tracked in one of these states:
        
           NEW_JOB 
           CHECKING_RESOURCES
           IN_READY_STATE
           STANDBY
           START_READOUT
           FINISH_READOUT
           COMPLETE
        """
        LOGGER.info('Setting up JobScoreboard')
        self._redis = self.connect()
        self._redis.flushdb()
        #DEBUG_ONLY:
        #self.charge_database()

        weekday = subprocess.check_output('date +"%u"', shell=True)
        job_num_seed = str(weekday) + "000"
        #set up auto sequence
        self._redis.set(self.JOB_SEQUENCE_NUM, job_num_seed)
      
    

    def connect(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=self.JOB_SCOREBOARD_DB)
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
            return False


    def get_next_job_num(self):
        if self.check_connection():
            self._redis.incr(self.JOB_SEQUENCE_NUM)
            return self._redis.get(self.JOB_SEQUENCE_NUM)
        else:
            LOGGER.error('Unable to increment job number due to lack of redis connection')
            #RAISE exception to catch in DMCS.py



    def add_job(self, job_number, rafts):
        """All job rows created in the scoreboard begin with this method
           where initial attributes are inserted.

           :param str job_number: Necessary for all CRUDs on this new row.
           :param int rafts: The number of 'sub-jobs' to be handled within a job.
        """
        job_num = str(job_number)
        # XXX Needs try, catch block
        if self.check_connection():
            self._redis.hset(job_num, self.RAFTS, rafts)
            self._redis.hset(job_num, self.STATE, 'NEW_JOB')
            self._redis.hset(job_num, 'JOB_CREATION_TIME', get_timestamp())
            self._redis.lpush(self.JOBS, job_num)
            #self.persist_snapshot()
        else:
            LOGGER.error('Unable to add new job; Redis connection unavailable')


    def set_job_params(self, job_number, params):
        """Sets a number of job row fields at once.

           :param str job_number: Cast as str below just in case an int type slipped in.
           :param dict params: A python dict of key/value pairs.
        """   
        if self.check_connection():
            job = str(job_number)
            for kee in params.keys():
                self._redis.hset(str(job), kee, params[kee])
        else:
            return False
        #self.persist_snapshot()


    def set_value_for_job(self, job_number, kee, val):
        """Set a specific field in a job row with a key and value.

           :param str job_number: Cast as str below.
           :param str kee: Represents the field (or key) to be set.
           :param str val: The value to be used for above key.
        """
        if self.check_connection():
            job = str(job_number) 
            return self._redis.hset(str(job), kee, val)
        else:
           return False

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
        if pairs:
            return yaml.load(pairs)
        else:
            return None


    def delete_job(self, job_number):
        #self._redis.hdel(self.JOBS, str(job_number))
        self._redis.lrem(self.JOBS, 0, str(job_number))


    def print_all(self):
        jobs = self._redis.lrange(self.JOBS, 0, -1)
        for job in jobs:
            x = self._redis.hgetall(job)
            print x


    def charge_database(self):
      pairs = {}
      other_pairs = {}
      #pairs = { 'F1':'D2', 'F2':'D6', 'F3':'D11', 'F4':'D1', 'F5':'D7'}
      pairs['F1'] = 'D2'
      pairs['F2'] = 'D6'
      pairs['F3'] = 'D11'
      pairs['F4'] = 'D1'
      pairs['F5'] = 'D7'
      other_pairs = { 'F1':'D10', 'F2':'D1', 'F3':'D11', 'F4':'D8', 'F5':'D4'}

      self.add_job(1,7,'ssh', '1k.test')
      self.add_job(2, 11,'rsync', '193k.test')
      self.add_job(3,1,'ftp', '16.7meg.test')
      self.add_job(4,7,'ssh', '1k.test')
      self.add_job(5, 11,'rsync', '193k.test')
      self.add_job(6,1,'ftp', '16.7meg.test')

      #self.set_pairs_for_job('1',  pairs)
      #self.set_pairs_for_job('2',  pairs)
      self.set_value_for_job('1', 'PAIRS', pairs)
      self.set_value_for_job('4', 'PAIRS', pairs)
      #self.set_value_for_job('5', 'PAIRS', pairs)
      #self.set_value_for_job('6', 'PAIRS', other_pairs)

      #keez = pairs.keys()
      #print("printing just keez")
      #print keez
      Ps = self.get_value_for_job(str(1), 'PAIRS')
      ppps = eval(Ps)
      print "final line"
      print ppps == pairs

def main():
  jbs = JobScoreboard()
  #Ps = jbs.get_value_for_job(str(1), 'PAIRS')
  #print "printing Ps"
  #print Ps
  #ppps = eval(Ps)
  #pps = ppps.keys()
  #print "final line"
  #print ppps == pairs



if __name__ == "__main__": main()
