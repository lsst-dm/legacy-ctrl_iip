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

@pytest.fixture(scope='session')
def bf(request):
    return BaseForeman('ForemanCfgTest.yaml')

logging.basicConfig(filename='logs/BaseForeman.log', level=logging.INFO, format=LOG_FORMAT)

class TestNCSAResourceQueryNegative:
    DMCS_PUBLISH = "dmcs_publish"
    DMCS_CONSUME = "dmcs_consume"
    NCSA_PUBLISH = "ncsa_publish"
    NCSA_CONSUME = "ncsa_consume"
    FORWARDER_PUBLISH = "forwarder_publish"
    F_CONSUME = "f_consume"
    ACK_PUBLISH = "ack_publish"
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'direct'
    PUB = None
    ACK_REPLACEMENT = "22_ZZ"
    CDM = None
    test_broker_url = None

    def setup_publisher(self):
        self.PUB = SimplePublisher(self.test_broker_url)

    def on_ncsa_resources_query(self, ch, method, properties, body):
        msg_dict = body

        msg_params = {}
        msg_params['MSG_TYPE'] = 'NCSA_RESOURCE_QUERY_ACK'
        msg_params['JOB_NUM'] = msg_dict[JOB_NUM]
        msg_params['ACK_BOOL'] = False
        msg_params['ACK_ID'] = self.ACK_REPLACEMENT
        msg_params['COMPONENT_NAME'] = 'NCSA_FOREMAN'
        msg_params['PAIRS'] = " "
        self.PUB.publish_message("ack_publish", msg_params)


    def run_consumer(self, threadname, delay, adict):
        callback = adict['cb']
        adict['csume'].run(callback)


    def setup_consumer(self, test_broker_url, Q, format, callback):
        consumer = Consumer(test_broker_url, Q, format)
        try:
            thread.start_new_thread( self.run_consumer, ("thread-test-consume", 2, {'csume': consumer, 'cb': callback}))
        except:
            print "Bad trouble creating consumer thread for testing...exiting..."
            sys.exit(101)


    def test_ncsa_resources_query_positive(self, bf):
        os.system('rabbitmqctl -p /tester purge_queue f_consume')
        os.system('rabbitmqctl -p /tester purge_queue forwarder_publish')
        os.system('rabbitmqctl -p /tester purge_queue ack_publish')
        try:
            f = open('ForemanCfgTest.yaml')
        except IOError:
            print "Can't open ForemanCfgTest.yaml"
            print "Bailing out on test_forwarder_check_health..."
            sys.exit(99)

        self.CDM = yaml.safe_load(f)
        number_of_pairs = self.CDM['ROOT']['NUMBER_OF_PAIRS']
        test_broker_address = self.CDM['ROOT']['TEST_BROKER_ADDR']
        name = self.CDM['ROOT']['TEST_BROKER_NAME']
        passwd = self.CDM['ROOT']['TEST_BROKER_PASSWD']
        forwarders = self.CDM['ROOT']['XFER_COMPONENTS']['FORWARDERS']
        f.close()

        self.test_broker_url = "amqp://" + name + ":" + passwd + "@" + str(test_broker_address)
        self.setup_publisher()
        self.setup_consumer(self.test_broker_url, 'ncsa_consume', 'XML', self.on_ncsa_resources_query)

        needed_forwarders = number_of_pairs - 1
        L = []
        for i in range (0, (needed_forwarders)):
            L.append(self.CDM['ROOT']['RAFT_LIST'][i])

        F = []
        keez = forwarders.keys()
        for i in range (0, (needed_forwarders)):
            F.append(keez[i])

        this_job_num = '24'

        params = {}
        params['MSG_TYPE'] = 'NEW_JOB'
        params['JOB_NUM'] = this_job_num
        params['ACK_ID'] = self.ACK_REPLACEMENT
        params['RAFTS'] = L


        bf.ncsa_resources_query(params, F)

        sleep(2)

        ack_responses = bf.ACK_SCBD.get_components_for_timed_ack(self.ACK_REPLACEMENT)

        assert len(ack_responses.keys()) == 1
        assert ack_responses['NCSA_FOREMAN']['ACK_BOOL'] == False
        print "Ack return time is: %s" % ack_responses['NCSA_FOREMAN']['ACK_RETURN_TIME']
        #assert ack_responses['NCSA_FOREMAN']['JOB_NUM'] == this_job_num

        #details = ack_responses[acker]['COMMENT']

        #assert details['NEEDED_FORWARDERS'] == needed_forwarders
        #assert details['AVAILABLE_FORWARDERS'] == available_forwarders
