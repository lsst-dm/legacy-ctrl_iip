import pika
import redis
import yaml
import sys
import os
from time import sleep
import thread
import pytest
import random

sys.path.insert(0, '../iip')
#sys.path.append('/home/fedora/src/git/ctrl_iip/python/lsst/iip')
from const import *
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

@pytest.fixture(scope='session')
def bf(request):
    return BaseForeman('ForemanCfgTest.yaml')

fman = bf

def setup_publisher(broker_url):
    publisher = SimplePublisher(broker_url)
    return publisher


def on_health_check_message(ch, method, properties, body):
    msg_dict = yaml.load(body)
    timed_ack = msg_dict["TIMED_ACK_ID"]
    job_num = msh_dict['JOB_NUM']
    msg_params = {}
    msg_params['MSG_TYPE'] = 'FORWARDER_HEALTH_ACK'
    msg_params['JOB_NUM'] = job_num
    msg_params['ACK_BOOL'] = True
    msg_params['ACK_ID'] = timed_ack
    msg_params['NAME'] = 'Forwarder_'
    publisher.publish_message("ack_publish", yaml.dump(msg_params))

def run_consumer(threadname, delay, adict):
    adict['csume'].run(on_health_check_message)


def setup_consumer(base_broker_url, f_consume):
    consumer = Consumer(base_broker_url, f_consume)
    try:
        thread.start_new_thread( run_consumer, ("thread-test-consume", 2, {'csume': consumer}))
    except:
        print "Bad trouble creating consumer thread for testing...exiting..."
        sys.exit(101)


def test_forwarder_check_health(fman):
    os.system('rabbitmqctl -p /tester purge_queue f_consume')
    os.system('rabbitmqctl -p /tester purge_queue forwarder_publish')
    #prep: create publisher and consumer
    #build params
    #inputs: job params
    #outputs: success or failure
    #intermediate worrys:
        # Sending health check to forwarders:
            #The foreman will handle this
            #for testing, he will use the SAME forwarder consume 
            #queue for each forwarder...spec'd in test CFG file   
            #
            #This test case file will generate the acks.
            #by watching the publish queue that ALL of the
            #forwarders will use, according to their conf files.
        #  
        # Receiving acks
            #then generate the appropriate responses.
        #
        # processing acks
            #the ack scoreboard will do receiving and processing.
        # this test case will check ack queue and compare
        # using the ack_id returned by the function
        #
        #
        # Close pub and consumer connection?

        ## Set up test cfg file
        #set up queue and permission creation
        #set up purge queue capability
        #put test forwarder_publish queue in CFG file
        #test case will need a publisher 
    #stuff
    try:
        f = open('ForemanCfgTest.yaml')
    except IOError:
        print "Can't open ForemanCfgTest.yaml"
        print "Bailing out on test_forwarder_check_health..."
        sys.exit(99)

    cdm = yaml.safe_load(f)
    number_of_pairs = cdm['ROOT']['NUMBER_OF_PAIRS']
    base_broker_address = cdm['ROOT']['BASE_BROKER_ADDR']
    name = cdm['ROOT']['BROKER_NAME']
    passwd = cdm['ROOT']['BROKER_PASSWD']
    base_broker_url = "amqp://" + name + ":" + passwd + "@" + str(base_broker_address)
    setup_consumer(base_broker_url, 'F_consume')
    publisher = setup_publisher(base_broker_url)
    forwarders = cdm['ROOT']['XFER_COMPONENTS']['FORWARDERS']

    #ack_scbd = bf.get_ack_scbd()

    #The test cfg file includes a list of all 21 rafts in non-consecutive order
    #The NUMBER_OF_PAIRS param is used to generate a sublist of above
    L = []
    for i in range (0, number_of_pairs):
        L.append(cdm['ROOT']['RAFT_LIST'][i]) 

    params = {}
    params['MSG_TYPE'] = 'NEW_JOB'
    params['JOB_NUM'] = str(7)
    params['RAFTS'] = L

    ack_id = fman.forwarder_health_check(params)
    sleep(3)
    ack_responses = fman.ACK_SCBD.get_components_for_timed_ack(ack_id)
    assert len(ack_responses) == int(number_of_pairs)

    print "ACK Responses are:"
    print ack_responses
    print "Done with forwarder_health_check test"



def test_insufficient_base_resources(fman):
    pass

def test_ncsa_resources_query(fman):
    pass

def test_distribute_job_params(fman):
    pass

def test_accept_job(fman):
    pass

def test_insufficient_ncsa_resources(fman):
    pass

def test_ncsa_no_response(fman):
    pass
