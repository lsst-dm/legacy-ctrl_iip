from const import *
import toolsmod
from toolsmod import get_timestamp
#from Consumer import Consumer
#import yaml
import time
import thread
import os
import sys
from influxdb import InfluxDBClient


class Influxator:

    def __init__(self):
        self.influx_client = InfluxDBClient('localhost', 8086)
        self.influx_client.switch_database('L1_Test')
        self.points = []
        point = { "measurement":"State",'entity':'fwd_4',"time":1478636564520880478, "fields": {'state':'unknown' }}
        point2 = { "measurement":"State",'entity':'fwd_5',"time":1478636564520880476, "fields": {'state':'idle' }}
        self.points.append(point)
        self.points.append(point2)
        self.influx_client.write_points(self.points)

#        self.broker_url = "amqp://BASE:BASE@141.142.208.191:5672/%2ftester"
#
#        self.influx_consumer = Consumer(self.broker_url, "influx_consume", "YAML")
#        try:
#            thread.start_new_thread( self.run_influx_consumer, ("thread-influx-consumer", 2,) )
#        except:
#            LOGGER.critical('Cannot start influx consumer thread, exiting...')
#            sys.exit(99)
#
#    def run_influx_consumer(self, threadname, delay):
#        self.influx_consumer.run(self.on_influx_message)
#
#
#
#    def on_influx_message(self, ch, method, properties, body):
#        self.process_data_for_influx(body)
#
#    def process_data_for_influx(self, body):
#        pass

def main():
    inf = Influxator()
    print "Influxator Done."


if __name__ == "__main__": main()

