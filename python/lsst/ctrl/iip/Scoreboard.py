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


from lsst.ctrl.iip.toolsmod import L1Error
from lsst.ctrl.iip.toolsmod import L1RabbitConnectionError
from lsst.ctrl.iip.AsyncPublisher import AsyncPublisher
import logging

LOGGER = logging.getLogger(__name__)


class Scoreboard:
    """This is the parent class of the three scoreboard classes.
       It, and they, form an interface for the Redis in-memory DB
       that continually stores state information about components and jobs.
    """

    AUDIT_QUEUE = 'audit_consume'

    def __init__(self, cred, cdm):

        self.cred = cred
        self.cdm = cdm

        broker_address = self.cdm['ROOT']['BASE_BROKER_ADDR']
        name = cred.getUser('service_user')
        passwd = cred.getUser('service_passwd')
        self.broker_url = "amqp://%s:%s@%s" % (name, passwd, broker_address)

        self.audit_format = "YAML"
        if 'AUDIT_MSG_FORMAT' in self.cdm['ROOT']:
            self.audit_format = self.cdm['ROOT']['AUDIT_MSG_FORMAT']

        try:
            self.audit_publisher = AsyncPublisher(self.broker_url, "audit_publisher")
            self.audit_publisher.start()
        except L1RabbitConnectionError as e:
            LOGGER.error("Scoreboard Parent Class cannot create AsyncPublisher:  ", e.arg)
            raise L1Error('Cant create AsyncPublisher'. e.arg)

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
