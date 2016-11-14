from const import *
import toolsmod
from toolsmod import get_timestamp
from Consumer import Consumer
import yaml
import time
import thread
import os
import sys
from influxdb import InfluxDBClient


class AuditListener:

    def __init__(self, filename=None):
        if filename == None:
            file = 'ForemanCfgTest.yaml'
        try:
            f = open(file)
        except IOError:
            print "Can't open %s" % file
            raise L1Error

        self.cdm = yaml.safe_load(f)

        broker_address = self.cdm['ROOT']['BASE_BROKER_ADDR']
        name = self.cdm['ROOT']['BASE_BROKER_NAME']
        passwd = self.cdm['ROOT']['BASE_BROKER_PASSWD']
        self.broker_url = "amqp://" + name + ":" + passwd + "@" + str(broker_address)
        self.influx_db = self.cdm['ROOT']['INFLUX_DB']
        self.monitor_format = "YAML"
        if 'MONITOR_MSG_FORMAT' in self.cdm['ROOT']:
            self.monitor_format = self.cdm['ROOT']['MONITOR_MSG_FORMAT']


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

        self.start_consumer(self.broker_url, self.monitor_format)


    def start_consumer(self, broker_url, format): 

        self.influx_consumer = Consumer(self.broker_url, "monitor_consume", "YAML")
        try:
            thread.start_new_thread( self.run_influx_consumer, ("thread-influx-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start influx consumer thread, exiting...')
            sys.exit(99)


    def run_influx_consumer(self, threadname, delay):
        self.influx_consumer.run(self.on_influx_message)


    def on_influx_message(self, ch, method, properties, msg):
        handler = self.msg_actions.get(msg['DATA_TYPE'])
        result = handler(msg)



    def process_ack_scbd(self, msg):
        tags_dict = {}
        tags_dict['ack_type'] = msg['SUB_TYPE']
        tags_dict['component'] = msg['COMPONENT_NAME']

        fields_dict = {}
        fields_dict['ack_id'] = msg['ACK_ID']

        if_dict = {}
        if_dict["measurement:" + str(msg['ACK_ID'])]
        if_dict["time"] = msg['TIME']
        if_dict["tags"] = tags_dict
        if_dict["fields"] = fields_dict
        self.influx_client.write_points(if_dict)

    def process_dist_scbd(self, body):
        pass

    def process_fwd_scbd(self, msg):
        pass


    def process_job_scbd(self, msg):
        handler = self.job_sub_actions(msg['SUB_TYPE'])
        result = handler(msg)


    def process_job_state(self, msg):
        tags_dict = {}
        tags_dict['job'] = msg['JOB_NUM']
        tags_dict['session'] = msg['SESSION_ID']
        tags_dict['visit'] = msg['VISIT_ID']

        fields_dict = {}
        fields_dict['state'] = msg['STATE']

        if_dict = {}
        if_dict["measurement:" + str(msg['SUB_TYPE'])]
        if_dict["time"] = msg['TIME']
        if_dict["tags"] = tags_dict
        if_dict["fields"] = fields_dict
        self.influx_client.write_points(if_dict)


    def process_job_status(self, msg):
        tags_dict = {}
        tags_dict['job'] = msg['JOB_NUM']
        tags_dict['session'] = msg['SESSION_ID']
        tags_dict['visit'] = msg['VISIT_ID']

        fields_dict = {}
        fields_dict['status'] = msg['STATUS']

        if_dict = {}
        if_dict["measurement":msg['SUB_TYPE']]
        if_dict["time"] = msg['TIME']
        if_dict["tags"] = tags_dict
        if_dict["fields"] = fields_dict
        self.influx_client.write_points(if_dict)


    def process_job_session(self, msg):
        fields_dict = {}
        fields_dict['session'] = msg['SESSION']

        if_dict = {}
        if_dict["measurement":msg['SUB_TYPE']]
        if_dict["time"] = msg['TIME']
        if_dict["fields"] = fields_dict
        self.influx_client.write_points(if_dict)


    def process_job_visit(self, msg):
        tags_dict = {}
        tags_dict['session'] = msg['SESSION_ID']

        fields_dict = {}
        fields_dict['visit'] = msg['VISIT']

        if_dict = {}
        if_dict["measurement":msg['SUB_TYPE']]
        if_dict["time"] = msg['TIME']
        if_dict["tags"] = tags_dict
        if_dict["fields"] = fields_dict
        self.influx_client.write_points(if_dict)


    def process_foreman_ack_request(self, msg):
        tags_dict = {}
        tags_dict['ack_type'] = msg['SUB_TYPE']
        tags_dict['component'] = msg['COMPONENT_NAME']

        fields_dict = {}
        fields_dict['ack_id'] = msg['ACK_ID']

        if_dict = {}
        if_dict["measurement":msg['SUB_TYPE']]
        if_dict["time"] = msg['TIME']
        if_dict["fields"] = fields_dict
        self.influx_client.write_points(if_dict)


    def process_job_pairs(self, msg):
        pass

    def process_dmcs_scbd(self, msg):
        pass

    def process_backlog_scbd(self, msg):
        pass




def main():
    al = AuditListener()
    time.sleep(2)
    print "AuditListener seems to be working all right."


if __name__ == "__main__": main()

