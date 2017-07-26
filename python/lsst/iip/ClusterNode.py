import pika
from Scratchpad import Scratchpad
from toolsmod import get_timestamp
from toolsmod import get_epoch_timestamp
import yaml
import sys
import time
import hashlib
import os.path
import logging
import os
import copy
import subprocess
import thread
from const import *
from Consumer import Consumer
from SimplePublisher import SimplePublisher


class ClusterNode:
    '''
        Name
        IP_ADDR
        CONSUME_QUEUE
        PUBLISH_QUEUE
        NCSA_BROKER_ADDR
    '''

    def __init__(self):
        f = open('ClusterNodeCfg.yaml')
        #cfg data map...
        cdm = yaml.safe_load(f)
        try:
            self._name = cdm['NODE_1'][NAME]
            self._passwd = cdm['NODE_1']['PASSWORD']
            self._ncsa_broker_addr = cdm['NODE_1']['NCSA_BROKER_ADDR']
            self._consume_queue = cdm['NODE_1']['CONSUME_QUEUE'] # c1_consume
            self._publish_queue = cdm['NODE_1']['PUBLISH_QUEUE'] # cluster_ctrl_ack_publish
            self._ip_addr = cdm['NODE_1']['IP_ADDR']

        except KeyError as e:
            print "Missing base keywords in yaml file... Bailing out..."
            sys.exit(99)

        self._ncsa_broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._ncsa_broker_addr)

        self._msg_actions = { 'CLUSTER_HEALTH_CHECK': self.process_cluster_health_check, 
			      'SEND_PARAMS': self.process_send_params } 

        self.setup_publishers()
        self.setup_consumers()


    def setup_publishers(self):
        self._publisher = SimplePublisher(self._ncsa_broker_url)

 
    def setup_consumers(self):
        threadname = "thread-" + self._consume_queue
        print "Threadname is %s" % threadname

        self._consumer = Consumer(self._ncsa_broker_url, self._consume_queue)
        try:
            thread.start_new_thread( self.run_consumer, (threadname, 2,) )
            print "Started Consumer Thread"
        except:
            sys.exit(99)


    def run_consumer(self, threadname, delay):
        self._consumer.run(self.on_message)


    def on_message(self, ch, method, properties, body):
        print "INcoming PARAMS, body is:\n%s" % body
        msg_dict = body

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


    def process_cluster_health_check(self, params):
        self.cluster_health_check_ack("CLUSTER_HEALTH_CHECK_ACK", params)


    def cluster_health_check_ack(self, type, params):
        timed_ack = params.get("ACK_ID")
        msg_params = {}
        msg_params[ACK_BOOL] = True
        msg_params[MSG_TYPE] = type
        msg_params[ACK_ID] = timed_ack
	msg_params['COMPONENT_NAME'] = self._name
        print "received__"
        self._publisher.publish_message(self._publish_queue, msg_params)


    def process_send_params(self, params):
	self.send_params_ack("SEND_PARAMS_ACK", params)


    def send_params_ack(self, type, params):
	timed_ack = params.get("ACK_ID")
	msg_params = {}
	msg_params["ACK_ID"] = timed_ack
	msg_params["MSG_TYPE"] = type
	msg_params["ACK_BOOL"] = True
	msg_params["COMPONENT_NAME"] = self._name
	self._publisher.publish_message(self._publish_queue, msg_params)


def main():
    cluster = ClusterNode()
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print ""
    print "Cluster Node Finished"


if __name__ == "__main__": main()


