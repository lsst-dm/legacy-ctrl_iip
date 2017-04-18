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
    JOB_STATUS = 'JOB_STATUS'
    STATUS = 'STATUS'
    SUB_TYPE = 'SUB_TYPE'
    JOB_SEQUENCE_NUM = 'JOB_SEQUENCE_NUM'
    SESSION_SEQUENCE_NUM = 'SESSION_SEQUENCE_NUM'
    CURRENT_SESSION_ID = 'CURRENT_SESSION_ID'
    DB_INSTANCE = None
    AR = "AR"
    PP = "PP"
    CU = "CU"
  

    def __init__(self, db_instance, ddict):
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
        job_num_seed = int(weekday) + 1000
        #set up auto sequence
        self._redis.set(self.JOB_SEQUENCE_NUM, int(job_num_seed))
        self._redis.set(self.SESSION_SEQUENCE_NUM, 70000)

        self.init_redis(ddict)
    

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


    def init_redis(self, ddict):
        if self.check_connection():
            self._redis.hset(self.AR, 'CONSUME_QUEUE', ddict[self.AR])
            self.set_device_state(self.AR, 'STANDBY')

            self._redis.hset(self.PP, 'CONSUME_QUEUE', ddict[self.PP])
            self.set_device_state(self.AR, 'STANDBY')

            self._redis.hset(self.CU, 'CONSUME_QUEUE', ddict[self.CU])
            self.set_device_state(self.CU, 'STANDBY')



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


    def get_device_state(self, device):
        if device == "AR":
            return self.get_archive_state()
        if device == "PP":
            return self.get_prompt_process_state()
        if device == "CU":
            return self.get_catchup_archive_state()


    def set_device_state(self, device, state):
        if device == "AR":
            return self.set_archive_state(state)
        if device == "PP":
            return self.set_prompt_process_state(state)
        if device == "CU":
            return self.set_catchup_archive_state(state)


    def get_device_consume_queue(self, device):
        if self.check_connection():
            if device == self.AR:
                return self._redis.hget(self.AR, "CONSUME_QUEUE")
            if device == self.PP:
                return self._redis.hget(self.PP, "CONSUME_QUEUE")
            if device == self.CU:
                return self._redis.hget(self.CU, "CONSUME_QUEUE")


    def get_devices_by_state(self, state):
        edict = {}
        if self.check_connection:
            if state == None:
                edict[self.AR] = self._redis.hget(self.AR, "CONSUME_QUEUE")
                edict[self.PP] = self._redis.hget(self.PP, "CONSUME_QUEUE")
                edict[self.CU] = self._redis.hget(self.CU, "CONSUME_QUEUE")
            else:
                if self.get_archive_state() == state:
                    edict[self.AR] = self._redis.hget(self.AR, "CONSUME_QUEUE")
                if self.get_prompt_process_state() == state:
                    edict[self.PP] = self._redis.hget(self.PP, "CONSUME_QUEUE")
                if self.get_catchup_archive_state() == state:
                    edict[self.CU] = self._redis.hget(self.CU, "CONSUME_QUEUE")
        else:
            print "BIG TROUBLE IN LITTLE CHINA"
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

        self._redis.rpush(listname, keys)


    def get_cfg_from_cfgs(self, device, index):
        # index 0 is the default
        if device == 'AR':
            listname = 'AR_CFG_KEYS'
        elif device == 'PP':
            listname = 'PP_CFG_KEYS'
        elif device == 'CU':
            listname = 'CU_CFG_KEYS'

        return self._redis.lindex(listname, index)


    def check_cfgs_for_cfg(self, device, cfg_key):
        if device == 'AR':
            listname = 'AR_CFG_KEYS'
        elif device == 'PP':
            listname = 'PP_CFG_KEYS'
        elif device == 'CU':
            listname = 'CU_CFG_KEYS'

        list_len = self._redis.llen(listname)
        if list_len == 0 or list_len == None:
            return True

        for item in range(0,list_len):
            if cfg_key == item:
                return True

        return False


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


    def get_current_session_id(self):
        if self.check_connection():
            return self._redis.get(self.CURRENT_SESSION_ID)
        else:
            LOGGER.error('Unable to increment job number due to lack of redis connection')
            #RAISE exception to catch in DMCS.py


    def get_next_job_num(self, prefix):
        if self.check_connection():
            self._redis.incr(self.JOB_SEQUENCE_NUM)
            job_num_str = prefix + str( self._redis.get(self.JOB_SEQUENCE_NUM))
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
