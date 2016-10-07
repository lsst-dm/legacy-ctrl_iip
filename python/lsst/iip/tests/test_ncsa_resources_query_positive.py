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


f = open('ForemanCfgTest.yaml')
x = yaml.safe_load(f)
#base_broker_url = "amqp://" + "TesT" + ":" + "TesT" + "@" + str(x['ROOT']['BASE_BROKER_ADDR'])
#def pb(request):
#    return SimplePublisher(base_broker_url)


logging.basicConfig(filename='logs/BaseForeman.log', level=logging.INFO, format=LOG_FORMAT)

PUB = None

def setup_publisher(test_broker_url):
    #print "In setup_publisher, printing PUB: "
    PUB = SimplePublisher(test_broker_url)
    #print PUB
    #print "Done printing PUB"
    #publisher = SimplePublisher(broker_url)
    #return PUB

def on_ncsa_resources_query(ch, method, properties, body):
    test_broker_url = "amqp://" + "TesT" + ":" + "TesT" + "@" + "141.142.208.191:5672/%2ftester"
    print "Creating publisher in on_ncsa_resources_query"
    publisher = SimplePublisher(test_broker_url)
    msg_dict = body
    forwarder_dict = yaml.load(msg_dict['FORWARDERS'])
    print "Printing FORWARDERS dict"
    #print msg_dict['FORWARDERS']
    print forwarder_dict
    #print "Index 28 is %s" % forwarder_dict[28]
    #print "Index 29 is %s" % forwarder_dict[29]
    #print "Index 30 is %s" % forwarder_dict[30]
    #print "Index 31 is %s" % forwarder_dict[31]
    #print "Index 32 is %s" % forwarder_dict[32]
    print "DONE printing FORWARDERS dict"
    try:
        f = open('ForemanCfgTest.yaml')
    except IOError:
        print "Can't open ForemanCfgTest.yaml"
        print "Bailing out on test_forwarder_check_health..."
        sys.exit(99)

    cdm = yaml.safe_load(f)
    distributors = cdm['ROOT']['XFER_COMPONENTS']['DISTRIBUTORS']
    pairs = {}
    keez = forwarder_dict.keys()
    dee_keez = distributors.keys()
    num_forwarders = len(keez)
    for i in range (0, num_forwarders):
        mini_dict = {}
        distributor = dee_keez[i]
        mini_dict['FQN'] = distributor
        mini_dict['NAME'] = distributors[dee_keez[i]]['NAME']
        mini_dict['HOSTNAME'] = distributors[dee_keez[i]]['HOSTNAME']
        mini_dict['IP_ADDR'] = distributors[dee_keez[i]]['IP_ADDR']
        mini_dict['TARGET_DIR'] = distributors[dee_keez[i]]['TARGET_DIR']
        mini_dict['RAFT'] = forwarder_dict[keez[i]]
        #print "Minidict this time is: "
        #print mini_dict
        pairs[keez[i]] = mini_dict
    

    timed_ack = msg_dict["ACK_ID"]
    msg_params = {}
    msg_params['MSG_TYPE'] = 'NCSA_RESOURCES_QUERY_ACK'
    msg_params['JOB_NUM'] = msg_dict[JOB_NUM]
    msg_params['ACK_BOOL'] = True
    msg_params['ACK_ID'] = msg_dict[ACK_ID]
    msg_params['COMPONENT_NAME'] = 'NCSA_FOREMAN'
    msg_params['PAIRS'] = yaml.dump(pairs)
    #hearst.publish_message("ack_publish", msg_params)
    publisher.publish_message("ack_publish", msg_params)


def run_consumer(threadname, delay, adict):
    callback = adict['cb']
    adict['csume'].run(callback)


def setup_consumer(test_broker_url, Q, format, callback):
    consumer = Consumer(test_broker_url, Q, format)
    try:
        thread.start_new_thread( run_consumer, ("thread-test-consume", 2, {'csume': consumer, 'cb': callback}))
    except:
        print "Bad trouble creating consumer thread for testing...exiting..."
        sys.exit(101)


def test_ncsa_resources_query_positive(bf):
    os.system('rabbitmqctl -p /tester purge_queue f_consume')
    os.system('rabbitmqctl -p /tester purge_queue forwarder_publish')
    os.system('rabbitmqctl -p /tester purge_queue ack_publish')
    try:
        f = open('ForemanCfgTest.yaml')
    except IOError:
        print "Can't open ForemanCfgTest.yaml"
        print "Bailing out on test_forwarder_check_health..."
        sys.exit(99)

    cdm = yaml.safe_load(f)
    number_of_pairs = cdm['ROOT']['NUMBER_OF_PAIRS']
    test_broker_address = cdm['ROOT']['TEST_BROKER_ADDR']
    name = cdm['ROOT']['TEST_BROKER_NAME']
    passwd = cdm['ROOT']['TEST_BROKER_PASSWD']
    forwarders = cdm['ROOT']['XFER_COMPONENTS']['FORWARDERS']
    f.close()

    test_broker_url = "amqp://" + name + ":" + passwd + "@" + str(test_broker_address)
    print "About to create publisher in test method"
    #hearst = setup_publisher(test_broker_url)
    #setup_publisher(test_broker_url)
    #print "hearst object prints out to be: "
    #print hearst
    #print "Done printing hearst"
    setup_consumer(test_broker_url, 'ncsa_consume', 'XML', on_ncsa_resources_query)

    #The test cfg file includes a list of all 21 rafts in non-consecutive order
    #The NUMBER_OF_PAIRS param is used to generate a sublist of above
    needed_forwarders = number_of_pairs - 1
    L = []
    for i in range (0, (needed_forwarders)):
        L.append(cdm['ROOT']['RAFT_LIST'][i])

    F = []
    keez = forwarders.keys()
    for i in range (0, (needed_forwarders)):
        F.append(keez[i])

    acker = '44'
    params = {}
    params['MSG_TYPE'] = 'NEW_JOB'
    params['JOB_NUM'] = '7'
    params['ACK_ID'] = acker
    params['RAFTS'] = L


    bf.ncsa_resources_query(params, F)

    sleep(3)

    #Fix below for new test......
    ack_responses = bf.ACK_SCBD.get_components_for_timed_ack(acker)

    assert len(ack_responses.keys()) == 1
    assert ack_responses['NCSA_FOREMAN']['ACK_BOOL'] == True
    print ack_responses['NCSA_FOREMAN']['ACK_RETURN_TIME']
    assert details['JOB_NUM'] == str(7)

    #details = ack_responses[acker]['COMMENT']

    #assert details['NEEDED_FORWARDERS'] == needed_forwarders
    #assert details['AVAILABLE_FORWARDERS'] == available_forwarders


#def test_distribute_job_params(fman):
#    pass
#
#def test_accept_job(fman):
#    pass
#
#def test_insufficient_ncsa_resources(fman):
#    pass
#
#def test_ncsa_no_response(fman):
###    pass
