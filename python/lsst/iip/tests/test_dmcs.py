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
import DMCS
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from const import *
import toolsmod

#from BaseForeman import *
from DMCS import *

"""
0) This test file works be sending the component to be tested, all of the messages
   it will receive, temporarily stores these messages for verification later,
   and sends the necessary responses to emulate other components that the 
   component being tested will communicate with. It also makes some database
   checks to insure the component being tested is doing proper
   bookkeeping.

This test file requires the use of two external servers:
1) An AMQP message broker
    a. There is a scripy in this directory called TestSetupRabbit.py that sets up
       the needed virtual hosts and the users, user permissions, and queues.
    b. The L1SysCfg_Test.yaml file should be edited to set the Rabbit address
       value in the BASE_BROKER_ADDR key

2) The Redis in-memory database. The database instances that are used for 
   each component are also found in L1SysCfg_Test.yaml

3) This test files tests the DMCS component. It is possible to include a specific
   Config file as the only argument when creating a DMCS object - for that matter,
   when creating ANY component object. Here we create the DMCS with the above
   mentioned L1SysCfg_Test.yaml file. When no argument is supplied at creation,
   the components use the default L1SysCfg.yaml file found in the iip/ dir.

4) This test can be used as template for any component tests. Right now,
   it checks component health by verifying the messages and acks the test 
   component sends. To use this file as a template for testing another component,
   simply create the Consumer objects using the appropriate queues, and then
   each Consumer plays the role of a component that the component being
   tested communicates with. Finally, the principal test method in this
   component test file sends messages to the component being tested.

   The messages sent exercise all messages received by the test component, and responses
   from the Consumers use the system glossary messages when responding.

5) Every time a consumer receives a message, it stores the message in a class
   List structure and then responds with the appropriate message.

   When this test file finishes sending messages, a RESET_TEST message type is sent
   to each consumer; then each consumer checks each message received and raises
   an exception if an error occurs.   

6) This test allows the DMCS component to behave EXACTLY as it will at run time - it
   is not aware that it is being tested. No special test artifacts exist within 
   component code.

"""
logging.basicConfig(filename='logs/DMCS_TEST.log', level=logging.INFO, format=LOG_FORMAT)

#@pytest.fixture(scope='session')
#def dmcs(request):
#    return DMCS('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test.yaml')

class TestDMCS:
#    @pytest.fixture(scope='session')
#    def dmcs(request):
#        return DMCS('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test.yaml')
    dmcs = DMCS('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test.yaml')

    ocs_pub_broker_url = None
    ocs_publisher = None
    ocs_consumer = None
    ocs_consumer_msg_list = []

    ar_pub_broker_url = None
    ar_publisher = None
    ar_consumer = None
    ar_consumer_msg_list = []

    pp_pub_broker_url = None
    pp_publisher = None
    pp_consumer = None
    pp_consumer_msg_list = []

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
      
        msg = {}
        msg['MSG_TYPE'] = 'RESET_TEST'
        time.sleep(5)
        print("RESET_TEST Message")
        self.ocs_publisher.publish_message("ar_foreman_consume", msg)
        self.ocs_publisher.publish_message("pp_foreman_consume", msg)
        self.ocs_publisher.publish_message("dmcs_ocs_publish", msg)
      
        time.sleep(8)

        print("Message Sender done")




    
    def on_ocs_message(self, ch, method, properties, body):
        print("Got an OCS Message")
    
    def on_ar_message(self, ch, method, properties, body):
        if body['MSG_TYPE'] == "RESET_TEST":
            ### Resolve messages for accuracy
            #del self.ar_consumer_msg_list
            len_list = len(self.ar_consumer_msg_list)
            if len_list != self.EXPECTED_AR_MESSAGES:
                raise Exception('AR simulator received incorrect number of messages.\nExpected %s but received %s' % (self.EXPECTED_AR_MESSAGES, len_list))

            # Now check num keys in each message first, then check for key errors
            for i in range(0, len_list):
                j = self.ar_consumer_msg_list[i]
                keez = list(self.ar_consumer_msg_list.keys())


            self.ar_consumer_msg_list = []
        else:
            self.ar_consumer_msg_list.append(body)
        #print("Got an AR Message: %s" % body)
        print("Current AR msg list is: %s" % self.ar_consumer_msg_list)
    
    def on_pp_message(self, ch, method, properties, body):
        print("Got an PP Message")

