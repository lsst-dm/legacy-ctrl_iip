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



from const import *
import toolsmod
from toolsmod import get_timestamp
from Consumer import Consumer
import yaml
import time
import _thread
import os
import sys
from influxdb import InfluxDBClient


class AuditListener:

    def __init__(self, filename=None):
        if filename == None:
            file = 'L1SystemCfg.yaml'
        try:
            f = open(file)
        except IOError:
            print("Can't open %s" % file)
            raise L1Error

        self.cdm = yaml.safe_load(f)

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

