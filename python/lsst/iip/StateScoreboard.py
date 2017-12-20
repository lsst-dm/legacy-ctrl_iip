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


###################################################
## This Scoreboard keeps track of the state of each device.
## It also generate Session IDs and Job Numbers, and keeps
## track of them.


class StateScoreboard(Scoreboard):
    JOBS = 'JOBS'
    SESSIONS = 'SESSIONS'
    VISITS = 'VISITS'
    JOB_NUM = 'JOB_NUM'
    WORKER_NUM = 'worker_num'
    STATE = 'STATE'
    JOB_STATE = 'JOB_STATE'
    JOB_STATUS = 'JOB_STATUS'
    VISIT_ID_LIST = 'VISIT_ID_LIST'
    STATUS = 'STATUS'
    SUB_TYPE = 'SUB_TYPE'
    JOB_SEQUENCE_NUM = 'JOB_SEQUENCE_NUM'
    SESSION_SEQUENCE_NUM = 'SESSION_SEQUENCE_NUM'
    CURRENT_SESSION_ID = 'CURRENT_SESSION_ID'
    DB_INSTANCE = None
    DB_TYPE = ""
    AR = "AR"
    PP = "PP"
    CU = "CU"
    SP = "SP"
  

    def __init__(self, db_type, db_instance, ddict):
        self.DB_TYPE = db_type
        self.DB_INSTANCE = db_instance
        self._session_id = str(1)
        try:
            Scoreboard.__init__(self)
        except L1RabbitConnectionError as e:
            LOGGER.error('Failed to make connection to Message Broker:  ', e.arg)
            print("No Monitoring for YOU")
            raise L1Error('Calling super.init in StateScoreboard init caused: ', e.arg)

        try:
            self._redis = self.connect()
        except L1RedisError as e:
            LOGGER.error("Cannot make connection to Redis:  " , e)  
            print("No Redis for YOU")
            raise L1Error('Calling redis connect in StateScoreboard init caused:  ', e.arg)

        self._redis.flushdb()

        weekday = subprocess.check_output('date +"%u"', shell=True).decode("utf-8")

        job_num_seed = int(weekday) + 1000
        #set up auto sequence
        self._redis.set(self.JOB_SEQUENCE_NUM, int(job_num_seed))
        self._redis.set(self.SESSION_SEQUENCE_NUM, 70000)

        self.init_redis(ddict)
    

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


    def init_redis(self, ddict):
        if self.check_connection():
            self._redis.hset(self.AR, 'CONSUME_QUEUE', ddict[self.AR])
            self.set_device_state(self.AR, 'STANDBY')

            self._redis.hset(self.PP, 'CONSUME_QUEUE', ddict[self.PP])
            self.set_device_state(self.PP, 'STANDBY')

            self._redis.hset(self.CU, 'CONSUME_QUEUE', ddict[self.CU])
            self.set_device_state(self.CU, 'STANDBY')

            self._redis.hset(self.SP, 'CONSUME_QUEUE', ddict[self.SP])
            self.set_device_state(self.SP, 'STANDBY')




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


    def set_spectrograph_state(self, state):
        if self.check_connection():
            self._redis.hset(self.SP, STATE, state)


    def get_spectrograph_state(self):
        if self.check_connection():
            return self._redis.hget(self.SP, STATE)


    def get_device_state(self, device):
        if device == "AR":
            return self.get_archive_state()
        if device == "PP":
            return self.get_prompt_process_state()
        if device == "CU":
            return self.get_catchup_archive_state()
        if device == "SP":
            return self.get_spectrograph_state()


    def set_device_state(self, device, state):
        if device == "AR":
            return self.set_archive_state(state)
        if device == "PP":
            return self.set_prompt_process_state(state)
        if device == "CU":
            return self.set_catchup_archive_state(state)
        if device == "SP":
            return self.set_spectrograph_state(state)


    def get_device_consume_queue(self, device):
        if self.check_connection():
            if device == self.AR:
                return self._redis.hget(self.AR, "CONSUME_QUEUE")
            if device == self.PP:
                return self._redis.hget(self.PP, "CONSUME_QUEUE")
            if device == self.CU:
                return self._redis.hget(self.CU, "CONSUME_QUEUE")
            if device == self.SP:
                return self._redis.hget(self.SP, "CONSUME_QUEUE")


    def get_devices_by_state(self, state):
        edict = {}
        if self.check_connection:
            if state == None:
                edict[self.AR] = self._redis.hget(self.AR, "CONSUME_QUEUE")
                edict[self.PP] = self._redis.hget(self.PP, "CONSUME_QUEUE")
                edict[self.CU] = self._redis.hget(self.CU, "CONSUME_QUEUE")
                edict[self.SP] = self._redis.hget(self.SP, "CONSUME_QUEUE")
            else:
                if self.get_archive_state() == state:
                    edict[self.AR] = self._redis.hget(self.AR, "CONSUME_QUEUE")
                if self.get_prompt_process_state() == state:
                    edict[self.PP] = self._redis.hget(self.PP, "CONSUME_QUEUE")
                if self.get_catchup_archive_state() == state:
                    edict[self.CU] = self._redis.hget(self.CU, "CONSUME_QUEUE")
                if self.get_spectrograph_state() == state:
                    edict[self.SP] = self._redis.hget(self.SP, "CONSUME_QUEUE")
        else:
            print("BIG TROUBLE IN LITTLE CHINA")
        return edict


    def get_devices(self):
        return self.get_devices_by_state(None)


    def set_device_cfg_key(self, device, key):
        self._redis.hset(device, 'CFG_KEY', key)


    def get_device_cfg_key(self, device):
        return self._redis.hget(device, 'CFG_KEY')


    def add_device_cfg_keys(self, device, keys):
        if device == 'AR':
            listname = 'AR_CFG_KEYS'
        elif device == 'PP':
            listname = 'PP_CFG_KEYS'
        elif device == 'CU':
            listname = 'CU_CFG_KEYS'
        elif device == 'SP':
            listname = 'SP_CFG_KEYS'

        self._redis.rpush(listname, keys)


    def get_cfg_from_cfgs(self, device, index):
        # index 0 is the default
        if device == 'AR':
            listname = 'AR_CFG_KEYS'
        elif device == 'PP':
            listname = 'PP_CFG_KEYS'
        elif device == 'CU':
            listname = 'CU_CFG_KEYS'
        elif device == 'SP':
            listname = 'SP_CFG_KEYS'

        return self._redis.lindex(listname, index)


    def check_cfgs_for_cfg(self, device, cfg_key):
        if device == 'AR':
            listname = 'AR_CFG_KEYS'
        elif device == 'PP':
            listname = 'PP_CFG_KEYS'
        elif device == 'CU':
            listname = 'CU_CFG_KEYS'
        elif device == 'SP':
            listname = 'SP_CFG_KEYS'

        list_len = self._redis.llen(listname)
        if list_len == 0 or list_len == None:
            return True

        list_keys = self._redis.lrange(listname, 0, -1)
        #for item in range(0,list_len):
        for item in list_keys:
            if cfg_key == item:
                return True

        return False


    def get_next_session_id(self):
        if self.check_connection():
            self._redis.incr(self.SESSION_SEQUENCE_NUM)
            session_id = self._redis.get(self.SESSION_SEQUENCE_NUM)
            #if device == "AR":
            #    self._redis.hset(self.AR, 'SESSION_ID', session_id)
            #if device == "PP":
            #    self._redis.hset(self.PP, 'SESSION_ID', session_id)
            #if device == "CU":
            #    self._redis.hset(self.CU, 'SESSION_ID', session_id)
            id = "Session_" + str(session_id)
            self._redis.set(self.CURRENT_SESSION_ID, id)
            return id
        else:
            LOGGER.error('Unable to increment job number due to lack of redis connection')
            #RAISE exception to catch in DMCS.py


    def get_current_session(self):
        if self.check_connection():
            return self._redis.get(self.CURRENT_SESSION_ID)
        else:
            LOGGER.error('Unable to retrieve current session ID due to lack of redis connection')
            #RAISE exception to catch in DMCS.py


    def set_visit_id(self, visit_id):
        if self.check_connection():
            self._redis.lpush(self.VISIT_ID_LIST, visit_id)
            params = {}
            params['SUB_TYPE'] = 'VISIT'
            params['VISIT_ID'] = visit_id
            #self.persist(self.build_monitor_data(params))


    def get_current_visit(self):
        if self.check_connection():
            return self._redis.lindex(self.VISIT_ID_LIST, 0)


    def get_next_job_num(self, prefix):
        if self.check_connection():
            self._redis.incr(self.JOB_SEQUENCE_NUM)
            job_num_str = prefix + str( self._redis.get(self.JOB_SEQUENCE_NUM))
            return job_num_str
        else:
            LOGGER.error('Unable to increment job number due to lack of redis connection')
            #RAISE exception to catch in DMCS.py

    def add_job(self, job_number, image_id, visit_id, ccds):
        """All job rows created in the scoreboard begin with this method
           where initial attributes are inserted.
        """
        if self.check_connection():
            self._redis.hset(job_number, 'IMAGE_ID', image_id)
            self._redis.hset(job_number, 'VISIT_ID', visit_id)
            self._redis.lpush(self.JOBS, job_number)
            self.set_ccds_for_job(job_number, ccds)
            self.set_job_state(job_number, 'NEW')
            self.set_value_for_job(job_number, STATUS, 'ACTIVE')
        else:
            LOGGER.error('Unable to add new job; Redis connection unavailable')
            #raise exception
            ### FIX add adit message?


    def set_job_state(self, job_number, state):
        if self.check_connection():
            self._redis.hset(job_number, STATE, state)
            #params = {}
            #params[JOB_NUM] = job_number
            #params['SUB_TYPE'] = self.JOB_STATE
            #params['STATE'] = state
            #params['IMAGE_ID'] = self._redis.hget(job_number, 'IMAGE_ID')
            #self.persist(self.build_monitor_data(params))


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
            else:
                self._redis.hset(job, kee, val)
            return True
        else:
           return False



    def set_current_device_job(self, job_number, device):
        try:
            if self.check_connection():
                if device == self.AR:
                    self._redis.lpush('AR_JOBS', job_number)
                if device == self.PP:
                    self._redis.lpush('PP_JOBS', job_number)
                if device == self.CU:
                    self._redis.lpush('CU_JOBS', job_number)
                if device == self.SP:
                    self._redis.lpush('SP_JOBS', job_number)
        except Exception as e:
            print("EXCEPTION in SET_CURRENT_DEVICE_JOB")
            print("Job Number is %s, Device is %s" % (job_number,device))
            print("Exception is %s" % e)


    def get_current_device_job(self, device):
        if self.check_connection():
            if device == self.AR:
                return self._redis.lindex('AR_JOBS', 0)
            if device == self.PP:
                return self._redis.lindex('PP_JOBS', 0)
            if device == self.CU:
                return self._redis.lindex('CU_JOBS', 0)
            if device == self.SP:
                return self._redis.lindex('SP_JOBS', 0)


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


    def set_results_for_job(self, job_number, results):
        if self.check_connection():
            self._redis.hset(str(job_number), 'RESULTS', yaml.dump(results))
            return True
        else:
            return False



    def build_monitor_data(self, params):
        monitor_data = {}
        keez = list(params.keys())
        for kee in keez:
            monitor_data[kee] = params[kee]
        monitor_data['SESSION_ID'] = self.get_current_session()
        monitor_data['VISIT_ID'] = self.get_current_visit()
        monitor_data['TIME'] = get_epoch_timestamp()
        monitor_data['DATA_TYPE'] = self.DB_TYPE
        return monitor_data


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
  jbs = StateScoreboard()
  print("State Scoreboard seems to be running OK")
  time.sleep(2)
  print("Done.")



if __name__ == "__main__": main()
