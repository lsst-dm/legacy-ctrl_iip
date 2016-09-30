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
from BaseForeman import *
from Scoreboard import Scoreboard
from ForwarderScoreboard import ForwarderScoreboard
from JobScoreboard import JobScoreboard
from AckScoreboard import AckScoreboard
from Consumer import Consumer
from SimplePublisher import SimplePublisher

"""
 Creates BaseForeman object used to test the methods below
 Can either last for the entire testing session or per test one can be created

This test file requires the use of two external fixtures:
1) An AMQP message broker
2) The Redis in-memory database

The BaseForeman class s built to receive parameters froma configuration file.
If an init arg is not given when creating a BaseForeman, the default
ForemanCFG.yaml is used...but it is also possible to create a BaseForeman
instance with a specific config file given as the arg - in this case, we will
use a file called ForemanCFGTest.yaml. This file contains the user/passwd
information for access to the message broker, and also gives explicit info
about the Forwarders that this file will use as well.

"""



class test_BaseForeman:
    FWD_SCBD = None
    JOB_SCBD = None
    ACK_SCBD = None
    DMCS_PUBLISH = "dmcs_publish"
    DMCS_CONSUME = "dmcs_consume"
    NCSA_PUBLISH = "ncsa_publish"
    NCSA_CONSUME = "ncsa_consume"
    FORWARDER_PUBLISH = "forwarder_publish"
    ACK_PUBLISH = "ack_publish"
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'direct'

    def __init__(self, filename=None):
        self._default_cfg_file = "ForemanCfgTest.yaml"
        if filename == None:
            filename = self._default_cfg_file

        try:
            f = open(filename)
        except: IOError:
            print "Can't open %s" % filename
            sys.exit(99)

        cdm = yaml.safe_load(f)
        self.number_of_pairs = cdm['ROOT'}{'NUMBER_OF_PAIRS']
        self.forwarders = cdm['ROOT']['XFER_COMPONENTS']['FORWARDERS']
        self.base_broker_address = cdm['ROOT']['BASE_BROKER_ADDR']
        self.ncsa_broker_address = cdm['ROOT']['NCSA_BROKER_ADDR']
        self.name = cdm['ROOT']['BROKER_NAME']
        self.passwd = cdm['ROOT']['BROKER_PASSWD']
        base_broker_url = "amqp://" + self.name + ":" + self.passwd + "@" + str(base_broker_address)
        ncsa_broker_url = "amqp://" + self.name + ":" + self.passwd + "@" + str(ncsa_broker_address)

        self.setup_publishers()
        self.setup_consumers()

    def setup_consumers(self):

        self.dmcs_consumer = Consumer(self.base_broker_url, "dmcs_consume", "XML")
        try:
            thread.start_new_thread( self.run_dmcs_consumer, ("thread-dmcs-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start DMCS consumer thread, exiting...')
            sys.exit(99)


        self._forwarder_consumer = Consumer(self._base_broker_url, "f_consume", "XML")
        try:
            thread.start_new_thread( self.run_forwarder_consumer, ("thread-forwarder-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start FORWARDERS consumer thread, exiting...')
            sys.exit(100)

############XXXXXXXXXXXX FIX BELOW THREAD STARTS

        self._ncsa_consumer = Consumer(self._base_broker_url, self.NCSA_PUBLISH, XML)
        try:
            thread.start_new_thread( self.run_ncsa_consumer, ("thread-ncsa-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start NCSA consumer thread, exiting...')
            sys.exit(101)


        self._ack_consumer = Consumer(self._base_broker_url, self.ACK_PUBLISH, XML)
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




