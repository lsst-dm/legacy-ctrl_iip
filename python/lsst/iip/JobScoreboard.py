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


class JobScoreboard(Scoreboard):
    """Extends parent Scoreboard class and provides initialization
       for Redis jobs table, each row being a new job.

       As seen as in the first class variable below, when the 
       connection to Redis is opened, the Job scoreboard is 
       assigned to Redis's rdDatabase instance 8. Redis launches with a default 
       15 separate database instances.
    """
    DBTYPE = 'JOB_SCOREBOARD_DB'
    JOBS = 'JOBS'
    SESSIONS = 'SESSIONS'
    VISITS = 'VISITS'
    JOB_NUM = 'JOB_NUM'
    WORKER_NUM = 'worker_num'
    RAFTS = 'RAFTS'
    JOB_STATE = 'JOB_STATE'
    STATE = 'STATE'
    JOB_STATUS = 'JOB_STATUS'
    STATUS = 'STATUS'
    SUB_TYPE = 'SUB_TYPE'
    JOB_SEQUENCE_NUM = 'JOB_SEQUENCE_NUM'
  

    def __init__(self):
        """After connecting to the Redis database instance 
           JOB_SCOREBOARD_DB, this redis database is flushed 
           for a clean start. A 'charge_database' method is 
           included for testing the module.

           Each job will be tracked in one of these states: 
           NEW 
           BASE_RESOURCES_QUERY
           BASE_INSUFFICIENT_RESOURCES
           NCSA_RESOURCES_QUERY
           NCSA_INSUFFICIENT_RESOURCES
           BASE_EVENT_PARAMS_SENT
           READY_FOR_EVENT
           READOUT
           READOUT_COMPLETE
           DELIVERY_COMPLETE
           SCRUBBED
           COMPLETE

           In addition, each job will have an assigned status:
           ACTIVE
           COMPLETE
           TERMINATED
        """
        LOGGER.info('Setting up JobScoreboard')
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

        weekday = subprocess.check_output('date +"%u"', shell=True)
        job_num_seed = str(weekday) + "000"
        #set up auto sequence
        self._redis.set(self.JOB_SEQUENCE_NUM, job_num_seed)
      
    

    def connect(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=JOB_SCOREBOARD_DB)
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


    def set_session(self, session_id):
        if self.check_connection():
            self._redis.rpush(self.SESSIONS, session_id)
            params = {}
            params['SUB_TYPE'] = 'SESSION'
            params['SESSION_ID'] = session_id
            params['DATA_TYPE'] = self.DBTYPE
            # skipping build_audit_data, so put TIME in here - see comment below
            params['TIME'] = get_epoch_timestamp()

            # Send directly without adding fields in 'build_audit_data', as no visit yet
            self.persist(params)


    def set_visit(self, visit_id):
        if self.check_connection():
            session_id = self.get_current_session()
            self._redis.rpush(session_id, visit_id)
            params = {}
            params['SUB_TYPE'] = 'VISIT'
            params['DATA_TYPE'] = self.DBTYPE
            self.persist(self.build_monitor_data(params))



    def add_job(self, job_number, image_id, rafts):
        """All job rows created in the scoreboard begin with this method
           where initial attributes are inserted.

           :param str job_number: Necessary for all CRUDs on this new row.
           :param int rafts: The number of 'sub-jobs' to be handled within a job.
        """
        job_num = str(job_number)
        # XXX Needs try, catch block
        if self.check_connection():
            self._redis.hset(job_num, self.RAFTS, rafts)
            self._redis.hset(job_num, self.STATE, 'NEW')
            self._redis.hset(job_num, self.STATUS, 'ACTIVE')
            self._redis.hset(job_num, 'IMAGE_ID', image_id)
            self._redis.hset(job_num, 'JOB_CREATION_TIME', get_timestamp())
            self._redis.lpush(self.JOBS, job_num)
            params = {}
            params[self.SUB_TYPE] = self.JOB_STATE
            params[JOB_NUM] = job_num
            params['IMAGE_ID'] = image_id
            params[self.STATE] = 'NEW'
            self.persist(self.build_monitor_data(params))

            params = {}
            params[self.SUB_TYPE] = self.JOB_STATUS
            params[JOB_NUM] = job_num
            params['IMAGE_ID'] = image_id
            params[self.STATUS] = 'active'
            self.persist(self.build_monitor_data(params))
        else:
            LOGGER.error('Unable to add new job; Redis connection unavailable')


    def set_job_params(self, job_number, in_params):
        """Sets a number of job row fields at once.

           :param str job_number: Cast as str below just in case an int type slipped in.
           :param dict params: A python dict of key/value pairs.
        """  
        if self.check_connection():
            job = str(job_number)
            for kee in in_params.keys():
                self._redis.hset(str(job), kee, in_params[kee])
            params = {}
            params[JOB_NUM] = job_number
            params['SUB_TYPE'] = self.JOB_STATE
            params['STATE'] = in_params['STATE']
            params['IMAGE_ID'] = self._redis.hget(job_number, 'IMAGE_ID')
            self.persist(self.build_monitor_data(params))
        else:
            return False

    def set_job_status(self, job_number, status):
        if self.check_connection():
            job = str(job_number)
            return self._redis.hset(job, self.STATUS, status)
            params = {}
            params[JOB_NUM] = job
            params[self.STATUS] = status
            params['IMAGE_ID'] = self._redis.hget(job_number, 'IMAGE_ID')
            self.persist(self.build_monitor_data(params))

    def set_value_for_job(self, job_number, kee, val):
        """Set a specific field in a job row with a key and value.

           :param str job_number: Cast as str below.
           :param str kee: Represents the field (or key) to be set.
           :param str val: The value to be used for above key.
        """
        if self.check_connection():
            job = str(job_number) 
            return self._redis.hset(job, kee, val)
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
        ### XXX FIX - Check for existence of pairs...
        if pairs:
            return yaml.load(pairs)
        else:
            return None


    def get_current_session(self):
        if self.check_connection():
            return self._redis.lindex(self.SESSIONS, 0)

    def get_current_visit(self):
        if self.check_connection():
            if self._redis.exists(self.get_current_session()):
                return self._redis.lindex(self.get_current_session(), 0)
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



    def set_session_id(self, session_id):
        self._session_id = str(session_id)


    def get_next_job_num(self):
        if self.check_connection():
            self._redis.incr(self.JOB_SEQUENCE_NUM)
            return self._redis.get(self.JOB_SEQUENCE_NUM)
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
