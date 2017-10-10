import pika
import redis
import yaml
import os
import sys
import pprint
from time import sleep
#import _thread
import threading
import pytest
import random
import logging
sys.path.insert(1, '../iip')
sys.path.insert(1, '../')
import DMCS
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from MessageAuthority import MessageAuthority
from const import *
import toolsmod

from DMCS import *

"""
0) This test file works be sending the component to be tested all of the messages
   it will receive. These messages are stored for verification later.
   Necessary responses are sent to emulate other components. 
   Some Redis database checks are made as well.

1) The test requires two external servers:
  A. An AMQP message broker
      a. There is a script in this directory called TestSetupRabbit.py that sets up
        the needed virtual hosts and the users, user permissions, and queues.
      b. The L1SysCfg_Test.yaml file should be edited to set the Rabbit address
        value and vhost to be used in the BASE_BROKER_ADDR key.

   B. The Redis in-memory database. The database instances that are used for 
      each component are also found in L1SysCfg_Test.yaml

2) This file tests the DMCS component. It is possible to include a specific
   Config file as the only argument when creating a DMCS object - for that matter,
   when creating ANY component object. Here we create the DMCS with the above
   mentioned L1SysCfg_Test.yaml file. When no argument is supplied at creation,
   the components use the default L1SysCfg.yaml file found in the iip/ dir.

3) This test file can be used as template for any component tests. Right now,
   it checks component health by verifying the messages and acks the test 
   component sends. To use this file as a template for testing another component,
   simply create the Consumer objects using the appropriate queues, and then
   each Consumer plays the role of a component that the component being
   tested communicates with. 

4) Every time a consumer receives a message, it stores the message in a class
   List structure and then responds with the appropriate message.

   When this test file finishes sending messages, each consumers messages are 
   are checked for the correct number received, and the messages are verified 
   with the MessageAuthority obj to confirm proper message contents. An exception 
   is thrown if an error occurs.

5) This test allows the DMCS component to behave EXACTLY as it will at run time - it
   is not aware that it is being tested. No special test artifacts exist within 
   component code.

"""
logging.basicConfig(filename='logs/DMCS_TEST.log', level=logging.INFO, format=LOG_FORMAT)


class TestDMCS_AR_PP:
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

    EXPECTED_AR_MESSAGES = 1
    EXPECTED_PP_MESSAGES = 1
    EXPECTED_OCS_MESSAGES = 1

    ccd_list = [14,17,21.86]
    prp = toolsmod.prp


    
    def test_dmcs(self):
        try:
            cdm = toolsmod.intake_yaml_file('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test.yaml')
        except IOError as e:
            trace = traceback.print_exc()
            emsg = "Unable to find CFG Yaml file %s\n" % self._config_file
            print(emsg + trace)
            sys.exit(101)
    
        broker_addr = cdm[ROOT]['BASE_BROKER_ADDR']
    
        ocs_name = cdm[ROOT]['OCS_BROKER_NAME']
        ocs_passwd = cdm[ROOT]['OCS_BROKER_PASSWD']
        ocs_pub_name = cdm[ROOT]['OCS_BROKER_PUB_NAME']
        ocs_pub_passwd = cdm[ROOT]['OCS_BROKER_PUB_PASSWD']
        ocs_broker_url = "amqp://" + ocs_name + ":" + \
                                 ocs_passwd + "@" + \
                                 broker_addr
        self. ocs_pub_broker_url = "amqp://" + ocs_pub_name + ":" + \
                                 ocs_pub_passwd + "@" + \
                                 broker_addr
        self.ocs_publisher = SimplePublisher(self.ocs_pub_broker_url, "YAML")
    
    
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

        # Must be done before consumer threads are started
        # This is used for verifying message structure
        self._msg_auth = MessageAuthority()


        self.ocs_consumer = Consumer(ocs_broker_url,'dmcs_ocs_publish', 'thread-ocs',
                                     self.on_ocs_message,'YAML', None)
        self.ocs_consumer.start()


        self.ar_consumer = Consumer(ar_broker_url,'ar_foreman_consume', 'thread-ar',
                                    self.on_ar_message,'YAML', None)
        self.ar_consumer.start()


        self.pp_consumer = Consumer(pp_broker_url,'pp_foreman_consume', 'thread-pp',
                                    self.on_pp_message,'YAML', None)
        self.pp_consumer.start()



        ### call message sender and pass in ocs_publisher
        sleep(3)
        print("Test Setup Complete. Commencing Messages...")

        self.send_messages()
        sleep(3)
        self.verify_ocs_messages()
        sleep(3)
        self.verify_ar_messages()
        sleep(3)
        self.verify_pp_messages()

        sleep(2)
        print("Finished with DMCS AR and PP tests.")
        #sys.exit


    def send_messages(self):

        print("Starting send_messages")
        # Tests both AR and PP devices
        
        self.EXPECTED_OCS_MESSAGES = 12
        self.EXPECTED_AR_MESSAGES = 7
        self.EXPECTED_PP_MESSAGES = 7

        self.clear_message_lists()

        msg = {}
        msg['MSG_TYPE'] = "STANDBY"
        msg['DEVICE'] = 'AR'
        msg['CMD_ID'] = '16729948'
        msg['CFG_KEY'] = "2C16"
        msg['ACK_ID'] = 'AR_4'
        msg['ACK_DELAY'] = 2
        time.sleep(1)
        print("AR STANDBY")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "STANDBY"
        msg['DEVICE'] = 'PP'
        msg['CMD_ID'] = '16729948'
        msg['CFG_KEY'] = "2C16"
        msg['ACK_ID'] = 'PP_7'
        msg['ACK_DELAY'] = 2
        time.sleep(5)
        print("PP STANDBY")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        #msg = {}
        #msg['MSG_TYPE'] = "NEW_SESSION"
        #msg['SESSION_ID'] = 'SI_469976'
        #msg['ACK_ID'] = 'NEW_SESSION_ACK_44221'
        #msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        ##time.sleep(1)
        ##self.ocs_publisher.publish_message("ar_foreman_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "DISABLE"
        msg['DEVICE'] = 'AR'
        msg['CMD_ID'] = '16729948'
        msg['ACK_ID'] = 'AR_6'
        msg['ACK_DELAY'] = 2
        time.sleep(5)
        print("AR DISABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "DISABLE"
        msg['DEVICE'] = 'PP'
        msg['CMD_ID'] = '16729948'
        msg['ACK_ID'] = 'PP_8'
        msg['ACK_DELAY'] = 2
        time.sleep(5)
        print("PP DISABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        # Make certain DMCS is doing proper bookkeeping
        sleep(6.5)
        assert self.dmcs.STATE_SCBD.get_archive_state() == 'DISABLE'
        assert self.dmcs.STATE_SCBD.get_prompt_process_state() == 'DISABLE'
      
        msg = {}
        msg['MSG_TYPE'] = "ENABLE"
        msg['DEVICE'] = 'AR'
        msg['CMD_ID'] = '16729948'
        msg['ACK_ID'] = 'AR_11'
        msg['ACK_DELAY'] = 2
        time.sleep(5)
        print("AR ENABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "ENABLE"
        msg['DEVICE'] = 'PP'
        msg['CMD_ID'] = '16729948'
        msg['ACK_ID'] = 'PP_12'
        msg['ACK_DELAY'] = 2
        time.sleep(5)
        print("PP ENABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)

        sleep(6.5)
        assert self.dmcs.STATE_SCBD.get_archive_state() == 'ENABLE'
        assert self.dmcs.STATE_SCBD.get_prompt_process_state() == 'ENABLE'
      
        msg = {}
        msg['MSG_TYPE'] = "NEXT_VISIT"
        msg['VISIT_ID'] = 'V_1443'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['ACK_ID'] = 'NEW_VISIT_ACK_76'
        msg['BORE_SIGHT'] = "231,123786456342, -45.3457156906, FK5"
        time.sleep(5)
        print("Next Visit Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)

        sleep(3.5)
        assert self.dmcs.STATE_SCBD.get_current_visit() == 'V_1443'
      
        msg = {}
        msg['MSG_TYPE'] = "START_INTEGRATION"
        msg['IMAGE_ID'] = 'IMG_4276'
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
      
        time.sleep(2)

        print("Message Sender done")


    def clear_message_lists(self):
        self.ocs_consumer_msg_list = []
        self.ar_consumer_msg_list = []
        self.pp_consumer_msg_list = []

    def verify_ocs_messages(self):
        print("Messages received by verify_ocs_messages:")
        self.prp.pprint(self.ocs_consumer_msg_list)
        len_list = len(self.ocs_consumer_msg_list)
        if len_list != self.EXPECTED_OCS_MESSAGES:
            print("Messages received by verify_ocs_messages:")
            self.prp.pprint(self.ocs_consumer_msg_list)
            pytest.fail('OCS simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_OCS_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.ocs_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                pytest.fail("The following OCS Bridge response message failed when compared with the sovereign example: %s" % msg)
        print("Responses to OCS Bridge pass verification.")
   

    def verify_ar_messages(self):
        print("Messages received by verify_ar_messages:")
        self.prp.pprint(self.ar_consumer_msg_list)
        len_list = len(self.ar_consumer_msg_list)
        if len_list != self.EXPECTED_AR_MESSAGES:
            print("Messages received by verify_ar_messages:")
            self.prp.pprint(self.ar_consumer_msg_list)
            pytest.fail('AR simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_AR_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.ar_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                pytest.fail("The following message to the AR failed when compared with the sovereign example: %s" % msg)
        print("Messages to the AR pass verification.")
   

    def verify_pp_messages(self):
        print("Messages received by verify_pp_messages:")
        self.prp.pprint(self.pp_consumer_msg_list)
        len_list = len(self.pp_consumer_msg_list)
        if len_list != self.EXPECTED_PP_MESSAGES:
            print("Messages received by verify_pp_messages:")
            self.prp.pprint(self.pp_consumer_list)
            pytest.fail('PP simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_PP_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.pp_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                pytest.fail("The following message to the PP device failed when compared with the sovereign example: %s" % msg)
        print("Messages to the PP device pass verification.")
   

    
    def on_ocs_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        self.ocs_consumer_msg_list.append(body)

 
    def on_ar_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        self.ar_consumer_msg_list.append(body)

    
    def on_pp_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        self.pp_consumer_msg_list.append(body)

