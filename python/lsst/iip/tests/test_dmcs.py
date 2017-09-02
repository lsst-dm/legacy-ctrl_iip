import pika
import redis
import yaml
import sys
import os
from time import sleep
import _thread
import pytest
import random
import logging
sys.path.insert(1, '../iip')
sys.path.insert(1, '../')
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from const import *
import toolsmod

#from BaseForeman import *
from DMCS import *

"""
 Creates DMCS object used to test the methods below
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
logging.basicConfig(filename='logs/DMCS.log', level=logging.INFO, format=LOG_FORMAT)

@pytest.fixture(scope='session')
def dmcs(request):
    return DMCS('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test.yaml')

class TestDMCS:
    ocs_pub_broker_url = None
    ocs_publisher = None
    ocs_consumer = None

    ar_pub_broker_url = None
    ar_publisher = None
    ar_consumer = None

    pp_pub_broker_url = None
    pp_publisher = None
    pp_consumer = None

    ccd_list = [14,17,21.86]


    def run_ocs_consumer(self, threadname, delay):
        self.ocs_consumer.run(self.on_ocs_message)
    
    def run_ar_consumer(self, threadname, delay):
        self.ar_consumer.run(self.on_ar_message)
    
    def run_pp_consumer(self, threadname, delay):
        self.pp_consumer.run(self.on_pp_message)
    
    
    def setup_consumers(self):
    
        try:
            _thread.start_new_thread( self.run_ocs_consumer, ("thread-test-ocs_consume", 2,) )
        except:
            print("Bad trouble creating ocs_consumer thread for testing...exiting...")
            sys.exit(101)
    
        try:
            _thread.start_new_thread( self.run_ar_consumer, ("thread-test-ar_consume", 2,) )
        except:
            print("Bad trouble creating ar_consumer thread for testing...exiting...")
            sys.exit(101)
    
        try:
            _thread.start_new_thread( self.run_pp_consumer, ("thread-test-pp_consume", 2,) )
        except:
            print("Bad trouble creating consumer thread for testing...exiting...")
            sys.exit(101)
    
    def test_dmcs(self):
        try:
            cdm = toolsmod.intake_yaml_file('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test.yaml')
        except IOError as e:
            trace = traceback.print_exc()
            emsg = "Unable to find CFG Yaml file %s\n" % self._config_file
            print(emsg + trace)
            sys.exit(101)
    
        broker_addr = cdm[ROOT]['BASE_BROKER_ADDR']
    
        ocs_name = cdm[ROOT]['BASE_BROKER_NAME']
        ocs_passwd = cdm[ROOT]['BASE_BROKER_PASSWD']
        ocs_pub_name = cdm[ROOT]['BASE_BROKER_PUB_NAME']
        ocs_pub_passwd = cdm[ROOT]['BASE_BROKER_PUB_PASSWD']
        ocs_broker_url = "amqp://" + ocs_name + ":" + \
                                 ocs_passwd + "@" + \
                                 broker_addr
        self. ocs_pub_broker_url = "amqp://" + ocs_pub_name + ":" + \
                                 ocs_pub_passwd + "@" + \
                                 broker_addr
        self.ocs_publisher = SimplePublisher(self.ocs_pub_broker_url, "YAML")
    
        pp_name = cdm[ROOT]['PFM_BROKER_NAME']
        pp_passwd = cdm[ROOT]['PFM_BROKER_PASSWD']
        pp_pub_name = cdm[ROOT]['PFM_BROKER_PUB_NAME']
        pp_pub_passwd = cdm[ROOT]['PFM_BROKER_PUB_PASSWD']
        pp_broker_url = "amqp://" + pp_name + ":" + \
                                pp_passwd + "@" + \
                                broker_addr
        self.pp_pub_broker_url = "amqp://" + pp_pub_name + ":" + \
                                    pp_pub_passwd + "@" + \
                                    broker_addr
        self.pp_publisher = SimplePublisher(self.pp_pub_broker_url, "YAML")
    
        ar_name = cdm[ROOT]['AFM_BROKER_NAME']
        ar_passwd = cdm[ROOT]['AFM_BROKER_PASSWD']
        ar_pub_name = cdm[ROOT]['AFM_BROKER_PUB_NAME']
        ar_pub_passwd = cdm[ROOT]['AFM_BROKER_PUB_PASSWD']
        ar_broker_url = "amqp://" + ar_name + ":" + \
                                ar_passwd + "@" + \
                                broker_addr
        self.ar_pub_broker_url = "amqp://" + ar_pub_name + ":" + \
                                    ar_pub_passwd + "@" + \
                                    broker_addr
        self.ar_publisher = SimplePublisher(self.ar_pub_broker_url, "YAML")
    
        self.ocs_consumer = Consumer(ocs_broker_url,'dmcs_ocs_publish', 'YAML')
        self.ar_consumer = Consumer(ar_broker_url,'ar_foreman_consume', 'YAML')
        self.pp_consumer = Consumer(pp_broker_url,'pp_foreman_consume', 'YAML')
    
        self.setup_consumers()
        ### call message sender and pass in ocs_publisher
        sleep(3)
        print("Test Setup Complete. Commencing Messages...")
        self.send_messages(1)
        assert 1

    def send_messages(self, test_num):
        

        msg = {}
        msg['MSG_TYPE'] = "STANDBY"
        msg['DEVICE'] = 'AR'
        msg['CFG_KEY'] = "2C16"
        msg['ACK_ID'] = 'AR_4'
        msg['ACK_DELAY'] = 2
        time.sleep(3)
        print("AR STANDBY")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "STANDBY"
        msg['DEVICE'] = 'PP'
        msg['CFG_KEY'] = "2C16"
        msg['ACK_ID'] = 'PP_7'
        msg['ACK_DELAY'] = 2
        time.sleep(3)
        print("PP STANDBY")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        #msg = {}
        #msg['MSG_TYPE'] = "NEW_SESSION"
        #msg['SESSION_ID'] = 'SI_469976'
        #msg['ACK_ID'] = 'NEW_SESSION_ACK_44221'
        #msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        ##time.sleep(3)
        ##self.ocs_publisher.publish_message("ar_foreman_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "DISABLE"
        msg['DEVICE'] = 'AR'
        msg['ACK_ID'] = 'AR_6'
        msg['ACK_DELAY'] = 2
        time.sleep(3)
        print("AR DISABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "DISABLE"
        msg['DEVICE'] = 'PP'
        msg['ACK_ID'] = 'PP_8'
        msg['ACK_DELAY'] = 2
        time.sleep(3)
        print("PP DISABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "ENABLE"
        msg['DEVICE'] = 'AR'
        msg['ACK_ID'] = 'AR_11'
        msg['ACK_DELAY'] = 2
        time.sleep(3)
        print("AR ENABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "ENABLE"
        msg['DEVICE'] = 'PP'
        msg['ACK_ID'] = 'PP_12'
        msg['ACK_DELAY'] = 2
        time.sleep(3)
        print("PP ENABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "NEXT_VISIT"
        msg['VISIT_ID'] = 'V_1443'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['ACK_ID'] = 'NEW_VISIT_ACK_76'
        msg['BORE_SIGHT'] = "231,123786456342, -45.3457156906, FK5"
        time.sleep(5)
        print("Next Visit Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "START_INTEGRATION"
        msg['IMAGE_ID'] = 'IMG_4276'
        msg['IMAGE_SRC'] = 'MAIN'
        msg['VISIT_ID'] = 'V_1443'
        msg['ACK_ID'] = 'START_INT_ACK_76'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['CCD_LIST'] = self.ccd_list
        time.sleep(5)
        print("Start Integration Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "READOUT"
        msg['VISIT_ID'] = 'V_1443'
        msg['IMAGE_ID'] = 'IMG_4276'
        msg['IMAGE_SRC'] = 'MAIN'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['ACK_ID'] = 'READOUT_ACK_77'
        time.sleep(5)
        print("READOUT Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "START_INTEGRATION"
        msg['IMAGE_ID'] = 'IMG_4277'
        msg['IMAGE_SRC'] = 'MAIN'
        msg['VISIT_ID'] = 'V_1443'
        msg['ACK_ID'] = 'START_INT_ACK_78'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['CCD_LIST'] = self.ccd_list
        time.sleep(5)
        print("Start Integration Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "READOUT"
        msg['VISIT_ID'] = 'V_1443'
        msg['IMAGE_ID'] = 'IMG_4277'
        msg['IMAGE_SRC'] = 'MAIN'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['ACK_ID'] = 'READOUT_ACK_79'
        time.sleep(5)
        print("READOUT Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        time.sleep(15)
      
        print("Message Sender done")




    
    def on_ocs_message(self, ch, method, properties, body):
        print("Got an OCS Message")
    
    def on_ar_message(self, ch, method, properties, body):
        print("Got an AR Message")
    
    def on_pp_message(self, ch, method, properties, body):
        print("Got an PP Message")

"""
def test_forwarder_check_health(fman):
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
    base_broker_address = cdm['ROOT']['BASE_BROKER_ADDR']
    name = cdm['ROOT']['BROKER_NAME']
    passwd = cdm['ROOT']['BROKER_PASSWD']
    base_broker_url = "amqp://" + name + ":" + passwd + "@" + str(base_broker_address)
    setup_publisher(base_broker_url)
    setup_consumer(base_broker_url, 'f_consume', 'XML')
    forwarders = cdm['ROOT']['XFER_COMPONENTS']['FORWARDERS']


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
    sleep(6)
    ack_responses = fman.ACK_SCBD.get_components_for_timed_ack(ack_id)
    assert ack_responses != None
    assert len(ack_responses) == int(number_of_pairs)
    print "Done with forwarder_health_check test"

"""
