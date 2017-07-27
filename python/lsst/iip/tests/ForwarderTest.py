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

sys.path.insert(0, '/home/AC/src/git/ctrl_iip/python/lsst/iip')
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

import Forwarder

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

@pytest.fixture(scope='session')
def fwd(request):
    return Forwarder.Forwarder()

class TestCases:

    ########### TEST HEALTH ##############
    def test_forwarder_check_health(self, fwd):
        # Set params
        params = {}
        params['MSG_TYPE'] = 'FORWARDER_HEALTH_CHECK'
        params['JOB_NUM'] = '563'
        params['ACK_ID'] = "11_BB"
        params['REPLY_QUEUE'] = "ack_publish"

        ack_responses = fwd.process_health_check(params)
        sleep(1)
        assert ack_responses != None
        assert ack_responses['ACK_BOOL'] == "TRUE"
        assert ack_responses['JOB_NUM'] == '563'
        assert ack_responses['MSG_TYPE'] == "FORWARDER_HEALTH_ACK"
        assert ack_responses['ACK_ID'] == "11_BB"
        assert ack_responses['COMPONENT_NAME'] == "FORWARDER_F1"

        print "PASSED HEALTH CHECK"

    ########### TEST PROCESS JOB ##############
    def test_process_job_params(self, fwd):
        params = {}
        minidict = {}
        minidict['NAME'] = "archive"
        minidict['IP_ADDR'] = "141.142.211.137"
        minidict['FQN'] = ""
        minidict['CCD_LIST'] = ["1","12","43","22"]
        params[MSG_TYPE] = 'AR_FWDR_XFER_PARAMS'
        params['XFER_PARAMS'] = minidict
        params['TARGET_DIR'] = "/dev/null/"
        params[ACK_ID] = "11_CC"
        params['REPLY_QUEUE'] = "ack_publish"
        params[JOB_NUM] = '563'
        params['IMAGE_ID'] = "image_1"
        params['SESSION_ID'] = "session_1"
        params['VISIT_ID'] = "visit_1"
        params['IMAGE_SRC'] = "temp_image_src"

        ack_responses = fwd.process_job_params(params)
        sleep(1)

	assert ack_responses['LOGIN_STR'] == "archive@141.142.211.137:"
	assert ack_responses['TARGET_DIR'] == "/dev/null/"
	assert ack_responses['FILENAME_STUB'] == "563_visit_1_image_1_"
	assert ack_responses['CCD_LIST'] == ["1","12","43","22"]

	print "Done checking job params"


    def test_fetch(self, fwd):
	job_num = "563"
	raw_files_dict = fwd.fetch(job_num).copy()


        sleep(1)

        assert raw_files_dict == {"1":"ccd_1.data", "12":"ccd_12.data",
                                  "43":"ccd_43.data", "22":"ccd_22.data"}

        print "Done checking fetch"


    def test_format(self, fwd):
        job_num = "563"
        raw_files_dict = fwd.fetch(job_num).copy()

        final_filenames = fwd.format(job_num, raw_files_dict)

        sleep(1)

        assert final_filenames == {"1":"563_visit_1_image_1__1.fits",
                                   "12":"563_visit_1_image_1__12.fits",
                                   "22":"563_visit_1_image_1__22.fits",
                                   "43":"563_visit_1_image_1__43.fits"}
        print "Done checking format"


    def test_forward(self, fwd):
        job_num = "563"
        raw_files_dict = fwd.fetch(job_num)
        final_filenames = fwd.format(job_num, raw_files_dict)
        result = fwd.forward(job_num, final_filenames)

        sleep(1)

        print(result)
        print("233333")



    def test_foreman_readout(self, fwd):
        params = {}
        params['MSG_TYPE'] = 'AR_READOUT'
        params['JOB_NUM'] = "563"
        params['SESSION_ID'] = "session_1"
        params['VISIT_ID'] = "visit_1"
        params['IMAGE_ID'] = "image_1"
        params['IMAGE_SRC'] = "temp_image_src"
        params['ACK_ID'] = "11_DD"
        params['RESPONSE_QUEUE'] = "ack_publish"

        ack_responses = fwd.process_foreman_readout(params)
        sleep(1)

        assert ack_responses['MSG_TYPE'] == 'AR_ITEMS_XFERD_ACK'
        assert ack_responses['JOB_NUM'] == "563"
        assert ack_responses['IMAGE_ID'] == "image_1"
        assert ack_responses['COMPONENT_NAME'] == "FORWARDER_F1"
        assert ack_responses['ACK_ID'] == "11_DD"
        assert ack_responses['ACK_BOOL'] == True
