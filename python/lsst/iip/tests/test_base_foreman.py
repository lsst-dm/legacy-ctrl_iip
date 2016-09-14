import pika
import redis
import yaml
import sys
import os
import thread
import pytest
import random

sys.path.insert(0, '../iip')
from const import *
from BaseForeman import *
from Scoreboard import Scoreboard
from ForwarderScoreboard import ForwarderScoreboard
from JobScoreboard import JobScoreboard
from AckScoreboard import AckScoreboard
from Consumer import Consumer
from SimplePublisher import SimplePublisher

# Creates BaseForeman object used to test the methods below
# Can either last for the entire testing session or per test one can be created

@pytest.fixture(scope='session')
def bf(request):
    return BaseForeman('ForemanCFGTest.yaml')

def test_forwarder_check_health(bf):
    stuff

def test_insufficient_base_resources(bf):
    stuff

def test_ncsa_resources_query(bf):
    stuff

def test_distribute_job_params(bf):
    stuff

def test_accept_job(bf):
    stuff

def test_insufficient_ncsa_resources(bf):
    stuff

def test_ncsa_no_response(bf):
    stuff
