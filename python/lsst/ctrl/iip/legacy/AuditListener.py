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


from lsst.ctrl.iip.const import *
import lsst.ctrl.iip.toolsmod
from lsst.ctrl.iip.toolsmod import get_timestamp
from lsst.ctrl.iip.Consumer import Consumer
import yaml
import time
import _thread
import os
import sys
import logging
from influxdb import InfluxDBClient

LOGGER = logging.getLogger(__name__)

class AuditListener(iip_base):

    def __init__(self, filename=None):

        self.cdm = self.loadConfigFile(filename)

        broker_address = self.cdm['ROOT']['BASE_BROKER_ADDR']
        name = self.cdm['ROOT']['AUDIT_BROKER_NAME']
        passwd = self.cdm['ROOT']['AUDIT_BROKER_PASSWD']
        self.broker_url = "amqp://" + name + ":" + passwd + "@" + str(broker_address)
        self.influx_db = 'MMM'
        #self.influx_db = self.cdm['ROOT']['INFLUX_DB']
        self.audit_format = "YAML"
        if 'AUDIT_MSG_FORMAT' in self.cdm['ROOT']:
            self.audit_format = self.cdm['ROOT']['AUDIT_MSG_FORMAT']


        self.msg_actions = { 'ACK_SCOREBOARD_DB': self.process_ack_scbd,
                             'DIST_SCOREBOARD_DB': self.process_dist_scbd,
                             'FWD_SCOREBOARD_DB': self.process_fwd_scbd,
                             'JOB_SCOREBOARD_DB': self.process_job_scbd,
                             'DMCS_SCOREBOARD_DB': self.process_dmcs_scbd,
                             'BACKLOG_SCOREBOARD_DB': self.process_backlog_scbd,
                             'FOREMAN_ACK_REQUEST': self.process_foreman_ack_request }

        self.job_sub_actions = { 'SESSION': self.process_job_session,
                                 'VISIT': self.process_job_visit,
                                 'JOB_STATE': self.process_job_state,
                                 'JOB_STATUS': self.process_job_status,
                                 'JOB_PAIRS': self.process_job_pairs}

        self.influx_client = InfluxDBClient('localhost', 8086)
        self.influx_client.switch_database(self.influx_db)

        self.start_consumer(self.broker_url, self.audit_format)


    def start_consumer(self, broker_url, format): 

        self.influx_consumer = Consumer(self.broker_url, "audit_consume", format)
        try:
            _thread.start_new_thread( self.run_influx_consumer, ("thread-influx-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start influx consumer thread, exiting...')
            sys.exit(99)


    def run_influx_consumer(self, threadname, delay):
        self.influx_consumer.run(self.on_influx_message)


    def on_influx_message(self, ch, method, properties, msg):
        #print "In audit, msg contents is:  %s" % msg
        ch.basic_ack(method.delivery_tag) 
        handler = self.msg_actions.get(msg['DATA_TYPE'])
        result = handler(msg)



    def process_ack_scbd(self, msg):
        L = []
        tags_dict = {}
        tags_dict['ack_type'] = msg['SUB_TYPE']
        tags_dict['component'] = msg['COMPONENT']
        tags_dict['job'] = msg['JOB_NUM']
        tags_dict['ack_id'] = msg['ACK_ID']
        tags_dict['image_id'] = msg['IMAGE_ID']

        fields_dict = {}
        fields_dict['ack_result'] = msg['ACK_BOOL']

        if_dict = {}
        if_dict["measurement"] = 'acks'
        if_dict["time"] = msg['TIME']
        if_dict["tags"] = tags_dict
        if_dict["fields"] = fields_dict
        L.append(if_dict)
        self.influx_client.write_points(L)

    def process_dist_scbd(self, body):
        pass

    def process_fwd_scbd(self, msg):
        pass


    def process_job_scbd(self, msg):
        handler = self.job_sub_actions.get(msg['SUB_TYPE'])
        result = handler(msg)


    def process_job_state(self, msg):
        L = []
        tags_dict = {}
        tags_dict['job'] = msg['JOB_NUM']
        tags_dict['session'] = msg['SESSION_ID']
        tags_dict['visit'] = msg['VISIT_ID']
        tags_dict['image_id'] = msg['IMAGE_ID']

        fields_dict = {}
        fields_dict['state'] = msg['STATE']

        if_dict = {}
        if_dict["measurement"] = msg['SUB_TYPE']
        if_dict["time"] = msg['TIME']
        if_dict["tags"] = tags_dict
        if_dict["fields"] = fields_dict
        L.append(if_dict)
        self.influx_client.write_points(L)


    def process_job_status(self, msg):
        L = []
        tags_dict = {}
        tags_dict['job'] = msg['JOB_NUM']
        tags_dict['session'] = msg['SESSION_ID']
        tags_dict['visit'] = msg['VISIT_ID']
        tags_dict['image_id'] = msg['IMAGE_ID']

        fields_dict = {}
        fields_dict['status'] = msg['STATUS']

        if_dict = {}
        if_dict["measurement"] = msg['SUB_TYPE']
        if_dict["time"] = msg['TIME']
        if_dict["tags"] = tags_dict
        if_dict["fields"] = fields_dict
        L.append(if_dict)
        self.influx_client.write_points(L)


    def process_job_session(self, msg):
        L = []
        tags_dict = {}
        tags_dict['sessions'] = "wha?"

        fields_dict = {}
        fields_dict['session'] = msg['SESSION_ID']

        if_dict = {}
        if_dict["measurement"] = msg['SUB_TYPE']
        if_dict["time"] = msg['TIME']
        if_dict["fields"] = fields_dict
        if_dict["tags"] = tags_dict
        L.append(if_dict)
        self.influx_client.write_points(L)


    def process_job_visit(self, msg):
        L = []
        tags_dict = {}
        tags_dict['session'] = msg['SESSION_ID']

        fields_dict = {}
        fields_dict['visit'] = msg['VISIT_ID']

        if_dict = {}
        if_dict["measurement"]= msg['SUB_TYPE']
        if_dict["time"] = msg['TIME']
        if_dict["tags"] = tags_dict
        if_dict["fields"] = fields_dict
        L.append(if_dict)
        self.influx_client.write_points(L)


    def process_foreman_ack_request(self, msg):
        L = []
        tags_dict = {}
        tags_dict['ack_type'] = msg['SUB_TYPE']
        tags_dict['component'] = msg['COMPONENT']

        fields_dict = {}
        fields_dict['ack_id'] = msg['ACK_ID']

        if_dict = {}
        if_dict["measurement"] = msg['SUB_TYPE']
        if_dict["time"] = msg['TIME']
        if_dict["fields"] = fields_dict
        L.append(if_dict)
        self.influx_client.write_points(L)


    def process_job_pairs(self, msg):
        pass

    def process_dmcs_scbd(self, msg):
        pass

    def process_backlog_scbd(self, msg):
        pass

    def run(self):
        print("Starting AuditListener...")
        while (1):
            pass


def main():
    al = AuditListener()

    try:
        al.run()
    except KeyboardInterrupt:
        print("AuditListener shutting down.")
        pass

#    time.sleep(2)
#    print "AuditListener seems to be working all right."



if __name__ == "__main__": main()

