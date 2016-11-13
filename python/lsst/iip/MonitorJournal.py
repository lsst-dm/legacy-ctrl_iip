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


class MonitorJournal:

    def __init__(self, filename=None):
        if filename == None:
            file = 'ForemanCfgTest.yaml'
        try:
            f = open(file)
        except IOError:
            print "Can't open %s" % file
            raise L1Error

        self.cdm = yaml.safe_load(f)

        broker_address = self.cdm['ROOT']['TEST_BROKER_ADDR']
        name = self.cdm['ROOT']['TEST_BROKER_NAME']
        passwd = self.cdm['ROOT']['TEST_BROKER_PASSWD']
        self.broker_url = "amqp://" + name + ":" + passwd + "@" + str(broker_address)
        self.monitor_format = "YAML"
        if 'MONITOR_MSG_FORMAT' in self.cdm['ROOT']:
            self.monitor_format = self.cdm['ROOT']['MONITOR_MSG_FORMAT']


        self.msg_actions = { 'ACK_SCOREBOARD_DB': self.process_ack_scbd,
                             'DIST_SCOREBOARD_DB': self.process_dist_scbd,
                             'FWD_SCOREBOARD_DB': self.process_fwd_scbd,
                             'JOB_SCOREBOARD_DB': self.process_job_scbd,
                             'DMCS_SCOREBOARD_DB': self.process_dmcs_scbd,
                             'BACKLOG_SCOREBOARD_DB': self.process_backlog_scbd}

        self.influx_client = InfluxDBClient('localhost', 8086)
        self.influx_client.switch_database('L1_Test')

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
        result = handler(body)



    def process_ack_scbd(self, body):
        pass

    def process_dist_scbd(self, body):
        pass

    def process_fwd_scbd(self, msg):
        pass

    def process_job_scbd(self, msg):
        tags_dict = {}
        tags_dict['job'] = msg['JOB_NUM']
        tags_dict['session_id'] = msg['SESSION_ID']

        fields_dict = {}
        if msg['SUB_TYPE'] == 'STATE':
            fields_dict['state'] = msg['STATE']
        elif msg['SUB_TYPE'] == 'STATUS':
            fields_dict['status'] = msg['STATUS']
        elif msg['SUB_TYPE'] == 'PAIRS':
            fields_dict['pairs'] = 'mates'
        else:
            fields_dict['pairs'] = '9999'

        if_dict = {}
        if_dict["measurement":msg['SUB_TYPE']]
        if_dict["time"] = msg['TIME']
        if_dict["tags"] = tags_dict
        if_dict["fields"] = fields_dict
        self.influx_client.write_points(if_dict)


    def process_dmcs_scbd(self, msg):
        pass

    def process_backlog_scbd(self, msg):
        pass




def main():
    mj = MonitorJournal()
    print "MonitorJournal finished."

#        self.points = []
#        point = { "measurement":"State",'entity':'fwd_4',"time":1478636564520880478, "fields": {'state':'unknown' }}
#        point2 = { "measurement":"State",'entity':'fwd_5',"time":1478636564520880476, "fields": {'state':'idle' }}
#        self.points.append(point)
#        self.points.append(point2)
#        self.influx_client.write_points(self.points)

if __name__ == "__main__": main()

