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
from toolsmod import get_timestamp
import logging
import pika
import redis
import yaml
import sys
import os
import time
from time import sleep
import _thread
from lsst.ctrl.iip.const import *
from lsst.ctrl.iip.Scoreboard import Scoreboard
from lsst.ctrl.iip.ForwarderScoreboard import ForwarderScoreboard
from lsst.ctrl.iip.JobScoreboard import JobScoreboard
from lsst.ctrl.iip.AckScoreboard import AckScoreboard
from lsst.ctrl.iip.Consumer import Consumer
from lsst.ctrl.iip.SimplePublisher import SimplePublisher

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class BaseForeman(iip_base):
    FWD_SCBD = None
    JOB_SCBD = None
    ACK_SCBD = None
    DMCS_PUBLISH = "dmcs_publish"
    DMCS_CONSUME = "dmcs_consume"
    NCSA_PUBLISH = "ncsa_publish"
    NCSA_CONSUME = "ncsa_consume"
    FORWARDER_PUBLISH = "forwarder_publish"
    ACK_PUBLISH = "ack_publish"
    YAML = 'YAML'
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'direct'
    SESSION_ID = 999
    CURRENT_VISIT = 111

######################################################
##  READ TYPE.YAML FIRST
######################################################

    def __init__(self, filename=None):
        toolsmod.singleton(self)

        cdm = self.loadConfigFile(filename)

        try:
            self._msg_name = cdm[ROOT][PFM_BROKER_NAME]      # Message broker user & passwd
            self._msg_passwd = cdm[ROOT][PFM_BROKER_PASSWD]   
            self._ncsa_name = cdm[ROOT][NCSA_BROKER_NAME]     
            self._ncsa_passwd = cdm[ROOT][NCSA_BROKER_PASSWD]   
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self._ncsa_broker_addr = cdm[ROOT][NCSA_BROKER_ADDR]
            forwarder_dict = cdm[ROOT][XFER_COMPONENTS][FORWARDERS]
        except KeyError as e:
            print("Dictionary error")
            print("Bailing out...")
            sys.exit(99)

        #if 'QUEUE_PURGES' in cdm[ROOT]:
        #    self.purge_broker(cdm['ROOT']['QUEUE_PURGES'])

        self._base_msg_format = self.YAML
        self._ncsa_msg_format = self.YAML

        if 'BASE_MSG_FORMAT' in cdm[ROOT]:
            self._base_msg_format = cdm[ROOT][BASE_MSG_FORMAT]

        if 'NCSA_MSG_FORMAT' in cdm[ROOT]:
            self._ncsa_msg_format = cdm[ROOT][NCSA_MSG_FORMAT]

        self._base_broker_url = 'amqp_url'
        self._ncsa_broker_url = 'amqp_url'
        self._next_timed_ack_id = 0


        # Create Redis Forwarder table with Forwarder info

        self.FWD_SCBD = ForwarderScoreboard(forwarder_dict)
        self.JOB_SCBD = JobScoreboard()
        self.ACK_SCBD = AckScoreboard()
        self._msg_actions = { 'NEW_JOB': self.process_dmcs_new_job,
                              'READOUT': self.process_dmcs_readout,
                              'NCSA_RESOURCE_QUERY_ACK': self.process_ack,
                              'NCSA_STANDBY_ACK': self.process_ack,
                              'NCSA_READOUT_ACK': self.process_ack,
                              'FORWARDER_HEALTH_ACK': self.process_ack,
                              'FORWARDER_JOB_PARAMS_ACK': self.process_ack,
                              'FORWARDER_READOUT_ACK': self.process_ack,
                              'NEW_JOB_ACK': self.process_ack }


        self._base_broker_url = "amqp://" + self._msg_name + ":" + self._msg_passwd + "@" + str(self._base_broker_addr)
        self._ncsa_broker_url = "amqp://" + self._ncsa_name + ":" + self._ncsa_passwd + "@" + str(self._ncsa_broker_addr)
        LOGGER.info('Building _base_broker_url. Result is %s', self._base_broker_url)
        LOGGER.info('Building _ncsa_broker_url. Result is %s', self._ncsa_broker_url)


    def setup_publishers(self):
        LOGGER.info('Setting up Base publisher on %s using %s', self._base_broker_url, self._base_msg_format)
        LOGGER.info('Setting up NCSA publisher on %s using %s', self._ncsa_broker_url, self._ncsa_msg_format)
        self._base_publisher = SimplePublisher(self._base_broker_url, self._base_msg_format)
        self._ncsa_publisher = SimplePublisher(self._ncsa_broker_url, self._ncsa_msg_format)


#    def setup_federated_exchange(self):
#        # Set up connection URL for NCSA Broker here.
#        self._ncsa_broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._ncsa_broker_addr)
#        LOGGER.info('Building _ncsa_broker_url. Result is %s', self._ncsa_broker_url)
#        pass


    def on_dmcs_message(self, ch, method, properties, body):
        #msg_dict = yaml.load(body) 
        msg_dict = body 
        LOGGER.info('In DMCS message callback')
        LOGGER.debug('Thread in DMCS callback is %s', _thread.get_ident())
        LOGGER.info('Message from DMCS callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def on_forwarder_message(self, ch, method, properties, body):
        LOGGER.info('In Forwarder message callback, thread is %s', _thread.get_ident())
        LOGGER.info('forwarder callback msg body is: %s', str(body))
        pass

    def on_ncsa_message(self,ch, method, properties, body):
        LOGGER.info('In ncsa message callback, thread is %s', _thread.get_ident())
        #msg_dict = yaml.load(body)
        msg_dict = body
        LOGGER.info('ncsa msg callback body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def on_ack_message(self, ch, method, properties, body):
        msg_dict = body 
        LOGGER.info('In ACK message callback')
        LOGGER.debug('Thread in ACK callback is %s', _thread.get_ident())
        LOGGER.info('Message from ACK callback message body is: %s', str(msg_dict))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def process_ack(self, params):
        self.ACK_SCBD.add_timed_ack(params)


    def set_session(self, params):
        self.SESSION_ID = params['SESSION_ID']


    def set_current_visit(self, params):
        self.CURRENT_VISIT = params['VISIT_ID']
        

    def get_next_timed_ack_id(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        retval = ack_type + "_" + str(self._next_timed_ack_id).zfill(6)
        return retval 


    def ack_timer(self, seconds):
        sleep(seconds)
        return True

    def purge_broker(self, queues):
        for q in queues:
            cmd = "rabbitmqctl -p /tester purge_queue " + q
            os.system(cmd)


def main():
    logging.basicConfig(filename='logs/BaseForeman.log', level=logging.INFO, format=LOG_FORMAT)
    b_fm = BaseForeman()
    print("Beginning BaseForeman event loop...")
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print("")
    print("Base Foreman Done.")



if __name__ == "__main__": main()
