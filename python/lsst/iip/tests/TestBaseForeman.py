import pika
import redis
import yaml
import sys
import os
from time import sleep
import thread
import pytest
import random
import logging

sys.path.insert(0, '../iip')
#sys.path.append('/home/fedora/src/git/ctrl_iip/python/lsst/iip')
from const import *
import toolsmod
from toolsmod import L1Exception
from toolsmod import L1MessageError
from toolsmod import get_timestamp
from BaseForeman import *
from Scoreboard import Scoreboard
from ForwarderScoreboard import ForwarderScoreboard
from JobScoreboard import JobScoreboard
from AckScoreboard import AckScoreboard
from Consumer import Consumer
from SimplePublisher import SimplePublisher

"""
 Creates BaseForeman object and is used by test methods below
 Can either last for the entire testing session or per test one can be created

This test file requires the use of two external fixtures:
1) An AMQP message broker
2) The Redis in-memory database

The BaseForeman class is built to receive parameters froma configuration file.
If an init arg is not given when creating a BaseForeman, the default
ForemanCFG.yaml is used...but it is also possible to create a BaseForeman
instance with a specific config file given as the arg - in this case, we will
use a file set up for testing purposes called ForemanCFGTest.yaml. 
This file contains the user/passwd information for access to the message 
broker, and also gives explicit info about the Forwarders that this file will 
use as well.

"""



class TestBaseForeman:
    FWD_SCBD = None
    JOB_SCBD = None
    ACK_SCBD = None
    DMCS_PUBLISH = "dmcs_publish"
    DMCS_CONSUME = "dmcs_consume"
    NCSA_PUBLISH = "ncsa_publish"
    NCSA_CONSUME = "ncsa_consume"
    FORWARDER_PUBLISH = "forwarder_publish"
    F_CONSUME = "f_consume"
    ACK_PUBLISH = "ack_publish"
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'direct'

    def __init__(self, filename=None):
        self.fman = BaseForeman("./ForemanCfgTest.yaml")
        sleep(3) #Give consumer threads a chance to spin up...
        self._default_cfg_file = "ForemanCfgTest.yaml"
        if filename == None:
            filename = self._default_cfg_file

        try:
            f = open(filename)
        except IOError:
            print "Can't open %s" % filename
            sys.exit(99)

        self.cdm = yaml.safe_load(f)
        self.number_of_pairs = self.cdm['ROOT']['NUMBER_OF_PAIRS']
        self.forwarders = self.cdm['ROOT']['XFER_COMPONENTS']['FORWARDERS']
        self.base_broker_address = self.cdm['ROOT']['BASE_BROKER_ADDR']
        self.ncsa_broker_address = self.cdm['ROOT']['NCSA_BROKER_ADDR']
        self.name = self.cdm['ROOT']['BROKER_NAME']
        self.passwd = self.cdm['ROOT']['BROKER_PASSWD']
        self.base_broker_url = "amqp://" + self.name + ":" + self.passwd + "@" + str(base_broker_address)
        self.ncsa_broker_url = "amqp://" + self.name + ":" + self.passwd + "@" + str(ncsa_broker_address)

        self.setup_publishers()
        self.setup_consumers()


    def setup_publishers(self):
        self.publisher = SimplePublisher(self.base_broker_url)


    def setup_consumers(self):
        """
        self.dmcs_consumer = Consumer(self.base_broker_url, DMCS_CONSUME, "XML")
        try:
            thread.start_new_thread( self.run_dmcs_consumer, ("thread-dmcs-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start DMCS consumer thread, exiting...')
            sys.exit(99)
        """

        self.forwarder_consumer = Consumer(self._base_broker_url, F_CONSUME, "XML")
        try:
            thread.start_new_thread( self.run_forwarder_consumer, ("thread-forwarder-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start FORWARDERS consumer thread, exiting...')
            sys.exit(100)

        """
        self._ncsa_consumer = Consumer(self._base_broker_url, self.NCSA_PUBLISH, XML)
        try:
            thread.start_new_thread( self.run_ncsa_consumer, ("thread-ncsa-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start NCSA consumer thread, exiting...')
            sys.exit(101)
        """

        self.ack_consumer = Consumer(self._base_broker_url, self.ACK_PUBLISH, XML)
        try:
            thread.start_new_thread( self.run_ack_consumer, ("thread-ack-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start ACK consumer thread, exiting...')
            sys.exit(102)


    def run_dmcs_consumer(self, threadname, delay):
        self.dmcs_consumer.run(self.on_dmcs_message)

    def on_dmcs_message(self, ch, method, properties, body):
        handler = self.msg_actions(body[MSG_TYPE])
        result = handler(body)


    def run_forwarder_consumer(self, threadname, delay):
        self.forwarder_consumer.run(self.on_forwarder_health_check_message)

    def on_forwarder_health_check_message(self, ch, method, properties, body):
        msg_dict = body
        timed_ack = msg_dict["ACK_ID"]
        job_num = msg_dict['JOB_NUM']
        msg_params = {}
        msg_params['MSG_TYPE'] = 'FORWARDER_HEALTH_ACK'
        msg_params['JOB_NUM'] = job_num
        msg_params['ACK_BOOL'] = True
        msg_params['ACK_ID'] = timed_ack
        msg_params['COMPONENT_NAME'] = 'Forwarder_' + str(get_timestamp())
        publisher.publish_message("ack_publish", msg_params)


    def run_ack_consumer(self, threadname, delay):
        self.ack_consumer.run(self.on_ack_message)


    """
       This test method does three things aside from performing
       the actual test:
           1) Creates a consumer that listen to a queue called 'f_consume'
              on the /tester exchange
              for the health checks the BaseForeman sends to Forwarders. ALL of
              the health checks are sent to this one queue by setting the
              ForemanCfgTest.yaml file forwarders to all have the same consume queue.
              This is OK as no forwarders are running during this test.
           2) Generates a message of type 'NEW_JOB' and gives it to the 
              BaseForeman.forwarder_health_check method for processing
           3) When the health chech requests arrive at the F_CONSUME queue,
              the test consumer sends appropriate acks to the 'ack_publish'
              queue - the BaseForeman Ack handler puts them in the AckScoreboard
              where they are viewed by this method.
    """

    def test_forwarder_check_health(self):
        os.system('rabbitmqctl -p /tester purge_queue f_consume')
        os.system('rabbitmqctl -p /tester purge_queue forwarder_publish')
        os.system('rabbitmqctl -p /tester purge_queue ack_publish')

        number_of_pairs = self.cdm['ROOT']['NUMBER_OF_PAIRS']
        forwarders = self.cdm['ROOT']['XFER_COMPONENTS']['FORWARDERS']


        #The test cfg file includes a list of all 21 rafts in non-consecutive order
        #The NUMBER_OF_PAIRS param is used to generate a sublist of above
        L = []
        for i in range (0, number_of_pairs):
            L.append(self.cdm['ROOT']['RAFT_LIST'][i])

        acker = str(42)
        params = {}
        params['MSG_TYPE'] = 'NEW_JOB'
        params['JOB_NUM'] = str(7)
        params['ACK_ID'] = acker
        params['RAFTS'] = L

        ack_id = self.fman.forwarder_health_check(params)
        sleep(3)
        ack_responses = self.fman.ACK_SCBD.get_components_for_timed_ack(ack_id)
        assert ack_responses != None
        assert len(ack_responses) == int(number_of_pairs)
        print "Done with forwarder_health_check test"

