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



import redis
import toolsmod
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
    JOBS = 'JOBS'
    SESSIONS = 'SESSIONS'
    VISIT_ID_LIST = 'VISIT_ID_LIST'
    JOB_NUM = 'JOB_NUM'
    WORKER_NUM = 'worker_num'
    RAFTS = 'RAFTS'
    JOB_STATE = 'JOB_STATE'
    STATE = 'STATE'
    JOB_STATUS = 'JOB_STATUS'
    STATUS = 'STATUS'
    SUB_TYPE = 'SUB_TYPE'
    RA = 'RA'
    DEC = 'DEC'
    ANGLE = 'ANGLE'
    JOB_SEQUENCE_NUM = 'JOB_SEQUENCE_NUM'
    CURRENT_SESSION_ID = 'CURRENT_SESSION_ID'
    DB_TYPE = ""
    DB_INSTANCE = None
    AR = 'AR'
    PP = 'PP'
    CU = 'CU'
    prp = toolsmod.prp
  

    def __init__(self, db_type, db_instance):
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
        self.DB_TYPE = db_type
        self.DB_INSTANCE = db_instance
        self._session_id = str(1)
        try:
            Scoreboard.__init__(self)
        except Exception as e:
            LOGGER.error('Job SCBD Auditor Failed to make connection to Message Broker:  ', e.arg)
            print("No Auditing for YOU")
            raise L1RabbitConnectionError('Calling super.init() in JobScoreboard init caused: ', e.arg)

        try:
            self._redis = self.connect()
        except Exception as e:
            LOGGER.error("Cannot make connection to Redis: %s." % e.arg)  
            print("Job SCBD: No Redis for YOU:")
            raise L1RedisError('Calling redis connect in JobScoreboard init caused:  ', e.arg)

        self._redis.flushdb()

        self._redis.set(self.CURRENT_SESSION_ID, "session_100")

#        weekday = subprocess.check_output('date +"%u"', shell=True)
#        job_num_seed = str(weekday) + "000"
#        #set up auto sequence
#        self._redis.set(self.JOB_SEQUENCE_NUM, job_num_seed)
      
        LOGGER.info('JobScoreboard initialization is complete')
    

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
                LOGGER.info('Attempting to reconnect to Redis - all set now')
                return True
        else: 
            LOGGER.info('In add_job, could not reconnect to Redis after 3 attempts')
            raise L1RedisError
            return False



    def add_job(self, job_number, visit_id, raft_list, raft_ccd_list):
        """All job rows created in the scoreboard begin with this method
           where initial attributes are inserted.

           :param str job_number: Necessary for all CRUDs on this new row.
           :param int rafts: The number of 'sub-jobs' to be handled within a job.
        """
        # XXX Needs try, catch block
        if self.check_connection():
            self._redis.hset(job_number, 'VISIT_ID', visit_id)
            self._redis.lpush(self.JOBS, job_number)
            self.set_rafts_for_job(job_number, raft_list, raft_ccd_list)
            self.set_job_state(job_number, 'NEW')
            self.set_job_status(job_number, 'ACTIVE')
        else:
            LOGGER.error('Unable to add new job; Redis connection unavailable')


    def set_job_params(self, job_number, in_params):
        """Sets a number of job row fields at once.

           :param str job_number: Cast as str below just in case an int type slipped in.
           :param dict params: A python dict of key/value pairs.
        """  
        if self.check_connection():
            for kee in list(in_params.keys()):
                self._redis.hset(job_number, kee, in_params[kee])

            #params = {}
            #params[JOB_NUM] = job_number
            #params['SUB_TYPE'] = self.JOB_STATE
            #params['STATE'] = self.get_job_state(job_number)
            #params['IMAGE_ID'] = self._redis.hget(job_number, 'IMAGE_ID')
            #self.persist(self.build_monitor_data(params))
        else:
            LOGGER.error('Unable to set job params; Redis connection unavailable')
            return False

    def set_job_state(self, job_number, state):
        if self.check_connection():
            self._redis.hset(job_number, STATE, state)
            #params = {}
            #params[JOB_NUM] = job_number
            #params['SUB_TYPE'] = self.JOB_STATE
            #params['STATE'] = state
            #params['IMAGE_ID'] = self._redis.hget(job_number, 'IMAGE_ID')
            #self.persist(self.build_monitor_data(params))


    def get_job_state(self, job_number):
        if self.check_connection():
            return self._redis.hget(job_number, STATE)


    def set_job_status(self, job_number, status):
        if self.check_connection():
            job = str(job_number)
            result = self._redis.hset(job, self.STATUS, status)
            #params = {}
            #params[JOB_NUM] = job
            #params['SUB_TYPE'] = self.JOB_STATUS
            #params[self.STATUS] = status
            #params['IMAGE_ID'] = self._redis.hget(job_number, 'IMAGE_ID')
            #self.persist(self.build_monitor_data(params))
            return result


    def set_value_for_job(self, job_number, kee, val):
        """Set a specific field in a job row with a key and value.

           :param str job_number: Cast as str below.
           :param str kee: Represents the field (or key) to be set.
           :param str val: The value to be used for above key.
        """
        if self.check_connection():
            job = str(job_number) 
            if kee == 'STATE':
                self.set_job_state(job, val)
            elif kee == 'STATUS':
                self.set_job_status(job, val)
            else:
                self._redis.hset(job, kee, val)
            return True
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
            LOGGER.critical("ERROR: No pairs associated with JOB %s" % job_number)
            return None

    def set_rafts_for_job(self, job_number, raft_list, raft_ccd_list):
        rafts = {}
        rafts['RAFT_LIST'] = raft_list
        rafts['RAFT_CCD_LIST'] = raft_ccd_list
        if self.check_connection():
            self._redis.hset(str(job_number), 'RAFTS', yaml.dump(rafts))
            return True
        else:
            return False


    def get_rafts_for_job(self, job_number):
        if self.check_connection():
            rafts =  self._redis.hget(str(job_number), 'RAFTS')
        ### XXX FIX - Check for existence of pairs...
        if rafts:
            return yaml.load(rafts)
        else:
            return None


    def set_work_schedule_for_job(self, job_number, schedule):
        """The work schedule is a temporary relationship between Forwarders 
           and CCDs that lasts for one job. Note the use of yaml...
           Unlike python dicts, Redis is not a nested level database. For a 
           field to have a dict attached to it, it is necessary to serialize 
           the dict using yaml, json, or pickle. Pyyaml is already in use 
           for conf files.

           :param str job_number: cast as str below just to make certain.
           :param  dict schedule: A dictionary with two items - a 'FORWARDER_LIST']
                                  and a 'CCD_LIST' which is a list of lists. Every
                                  index in 'FORWARDER_LIST' matches an index position in
                                  'CCD_LIST' which contains a list of CCDs.
        """
        print("Setting work schedule...")
        if self.check_connection():
            self._redis.hset(str(job_number), 'WORK_SCHEDULE', yaml.dump(schedule))
            return True
        else:
            return False


    def get_work_schedule_for_job(self, job_number):
        if self.check_connection():
            sched =  self._redis.hget(str(job_number), 'WORK_SCHEDULE')

        if sched:
            return yaml.load(sched)
        else:
            return None


    def set_results_for_job(self, job_number, results):
        if self.check_connection():
            self._redis.hset(str(job_number), 'RESULTS', yaml.dump(results))
            return True
        else:
            return False


    def get_results_for_job(self, job_number):
        if self.check_connection():
            results =  self._redis.hget(str(job_number), 'RESULTS')
        if results:
            return yaml.load(results)
        else:
            return None


    def get_device_for_job(self, job_number):
        if self.check_connection():
            return self._redis.hget(job_number, 'DEVICE')
            

    def set_session(self, session_id):
        self._redis.set(self.CURRENT_SESSION_ID, session_id)


    def get_current_session(self):
        return self._redis.get(self.CURRENT_SESSION_ID)


    def set_visit_id(self, visit_id, ra, dec, angle):
        if self.check_connection():
            print("In job scbd, setting visit ID")
            self._redis.lpush(self.VISIT_ID_LIST, visit_id)
            self._redis.hset(visit_id, self.RA, ra)
            self._redis.hset(visit_id, self.DEC, dec)
            self._redis.hset(visit_id, self.ANGLE, angle)
            #params = {}
            #params['SUB_TYPE'] = 'VISIT'
            #params['VISIT_ID'] = visit_id
            #params['BORE_SIGHT'] = bore_sight
            #self.persist(self.build_monitor_data(params))


    def get_current_visit(self):
        if self.check_connection():
            return self._redis.lindex(self.VISIT_ID_LIST, 0)


    def get_boresight_for_visit_id(self, visit_id):
        if self.check_connection():
            return self._redis.hget(visit_id, 'BORE_SIGHT')

             
    def delete_job(self, job_number):
        #self._redis.hdel(self.JOBS, str(job_number))
        self._redis.lrem(self.JOBS, 0, str(job_number))


    def build_monitor_data(self, params):
        monitor_data = {}
        keez = list(params.keys())
        for kee in keez:
            monitor_data[kee] = params[kee]
        monitor_data['SESSION_ID'] = self.get_current_session()
        monitor_data['VISIT_ID'] = self.get_current_visit()
        monitor_data['TIME'] = get_timestamp()
        monitor_data['DATA_TYPE'] = self.DB_TYPE
        return monitor_data


    def set_current_device_job(self, job_number, device):
        if self.check_connection():
            if device == self.AR:
                self._redis.rpush('AR_JOBS', job_number)
            if device == self.PP:
                self._redis.rpush('PP_JOBS', job_number)
            if device == self.CU:
                self._redis.rpush('CU_JOBS', job_number)


    def get_current_device_job(self, device):
        if self.check_connection():
            if device == self.AR:
                return self._redis.lindex('AR_JOBS', 0) 
            if device == self.PP:
                return self._redis.lindex('PP_JOBS', 0) 
            if device == self.CU:
                return self._redis.lindex('CU_JOBS', 0) 


    def print_all(self):
        dump_dict = {}
        f = open("dump", 'w')
        jobs = self._redis.lrange(self.JOBS, 0, -1)
        for job in jobs:
            x = self._redis.hgetall(job)
            dump_dict[job] = x

        f.write(yaml.dump(dump_dict))
        print(dump_dict)


def main():
  jbs = JobScoreboard()
  print("Job Scoreboard seems to be running OK")
  time.sleep(2)
  print("Done.")


if __name__ == "__main__": main()
