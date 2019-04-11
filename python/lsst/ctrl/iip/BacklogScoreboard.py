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
import logging
import time
import subprocess
from lsst.ctrl.iip.Scoreboard import Scoreboard
from lsst.ctrl.iip.const import *

LOGGER = logging.getLogger(__name__)


########################################################
## This Scoreboard keeps track of jobs or partial jobs
## that must be done. Backlog job items might be added
## because one or more CCDs were dropped during transfer
## or perhaps the Long Haul Network is down and jobs
## are queued in this scoreboard for transfer later.
## Finally, during the night, archiving may fall behind
## so archive jobs are added to the backlog scoreboard.
## A policy module will be used to determine how
## backlog jobs are sorted and the next job is
## chosen.


class BacklogScoreboard(Scoreboard):
    JOBS = 'JOBS'
    SESSIONS = 'SESSIONS'
    VISITS = 'VISITS'
    JOB_NUM = 'JOB_NUM'
    JOB_STATUS = 'JOB_STATUS'
    STATUS = 'STATUS'
    SUB_TYPE = 'SUB_TYPE'
    DB_TYPE = ""
  

    def __init__(self, db_type, db_instance):
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



    def add_job_to_backlog(self, params):
        # Params should include:
        # 1) Orig job number
        # 2) Type of job (AR, PP, etc)
        # 3) Priority
        # 4) Date/time when added
        # 5) Orig session_id
        # 6) Image_ID
        # 7) Visit_ID
        # 8) CCD list
        pass

    def get_backlog_stats(self):
        pass

    def get_backlog_details(self):
        pass

    def get_next_backlog_item(self):
        # Use policy module to sort jobs
        pass

    def get_waiting_time(self, job_num):
        pass



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




def main():
  bls = BacklogScoreboard()
  print("Backlog Scoreboard seems to be running OK")
  time.sleep(2)
  print("Done.")
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
