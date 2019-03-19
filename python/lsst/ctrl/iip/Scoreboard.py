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


import toolsmod
import time
import redis
from SimplePublisher import SimplePublisher
import sys
import yaml
import logging
import os
from iip_base import iip_base

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class Scoreboard(iip_base):
    """This is the parent class of the three scoreboard classes. 
       It, and they, form an interface for the Redis in-memory DB
       that continually stores state information about components and jobs.
    """

    AUDIT_QUEUE = 'audit_consume'

    def __init__(self, filename=None):

        self.cdm = self.loadConfigFile(filename)

        broker_address = self.cdm['ROOT']['BASE_BROKER_ADDR']
        name = self.cdm['ROOT']['BASE_BROKER_NAME']
        passwd = self.cdm['ROOT']['BASE_BROKER_PASSWD']
        self.broker_url = "amqp://" + name + ":" + passwd + "@" + str(broker_address)

        self.audit_format = "YAML"
        if 'AUDIT_MSG_FORMAT' in self.cdm['ROOT']:
            self.audit_format = self.cdm['ROOT']['AUDIT_MSG_FORMAT']

        try:
            self.audit_publisher = SimplePublisher(self.broker_url, self.audit_format)
        except L1RabbitConnectionError as e:
            LOGGER.error("Scoreboard Parent Class cannot create SimplePublisher:  ", e.arg)
            print("No Publisher for YOU")
            raise L1Error('Cant create SimplePublisher'. e.arg)


    def persist(self, data):
        self.audit_publisher.publish_message(self.AUDIT_QUEUE, data)


    def persist_snapshot(self, connection, filename):
        pass
        """
        LOGGER.info('Saving Scoreboard Snapshot')
        rdb = filename + ".rdb" 
        self._redis.config_set("dbfilename", rdb)
        while True: 
            try: 
                self._redis.bgsave()
                break
            except: 
                print("Waiting for preceding persistence to complete.")
                time.sleep(10) 


        while True: 
            if rdb in os.listdir(os.getcwd()): 
                os.rename(rdb, filename + "_" +  str(self._redis.lastsave()) + ".rdb")
                break
            else:
                print("Waiting for current persistence to complete.")
                time.sleep(10)
        """ 










