import pika
import redis
import yaml
import sys
import os
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

logging.basicConfig(filename='logs/DMCS_TEST.log', level=logging.INFO, format=LOG_FORMAT)

class TestDMCS_AR:
    dmcs = DMCS('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test.yaml')

    ocs_pub_broker_url = None
    ocs_publisher = None
    ocs_consumer = None
    ocs_consumer_msg_list = []

    ar_pub_broker_url = None
    ar_publisher = None
    ar_consumer = None
    ar_consumer_msg_list = []

    EXPECTED_AR_MESSAGES = 1
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
    
        # Must be done before consumer threads are started
        # This is used for verifying message structure
        self._msg_auth = MessageAuthority()

        self.ocs_consumer = Consumer(ocs_broker_url,'dmcs_ocs_publish', 'thread-ocs',
                                     self.on_ocs_message,'YAML', None)
        self.ocs_consumer.start()


        self.ar_consumer = Consumer(ar_broker_url,'ar_foreman_consume', 'thread-ar', 
                                    self.on_ar_message,'YAML', None)
        self.ar_consumer.start()

        sleep(3)
        print("Test Setup Complete. Commencing Messages...")

        self.send_messages()
        sleep(3)
        self.verify_ocs_messages()
        sleep(7)
        self.verify_ar_messages()

        sleep(2)
        print("Finished with DMCS AR tests.")
        #sys.exit(0)


    def send_messages(self):

        print("Starting send_messages")
        # Tests only an AR device
        
        self.clear_message_lists()

        self.EXPECTED_OCS_MESSAGES = 6
        self.EXPECTED_AR_MESSAGES = 5

        #msg = {}
        #msg['MSG_TYPE'] = "ENTER_CONTROL"
        #msg['DEVICE'] = 'AR'
        #msg['CMD_ID'] = '17718411'
        #msg['CFG_KEY'] = "2C16"
        #msg['ACK_ID'] = 'AR_4'
        #msg['ACK_DELAY'] = 2
        #time.sleep(2)
        #print("AR ENTER CONTROL")
        #self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "STANDBY"
        msg['DEVICE'] = 'AR'
        msg['CMD_ID'] = '17718411'
        msg['CFG_KEY'] = "2C16"
        msg['ACK_ID'] = 'AR_4'
        msg['ACK_DELAY'] = 2
        time.sleep(2)
        print("AR STANDBY")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "DISABLE"
        msg['DEVICE'] = 'AR'
        msg['CMD_ID'] = '17718411'
        msg['ACK_ID'] = 'AR_6'
        msg['ACK_DELAY'] = 2
        time.sleep(2)
        print("AR DISABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)

        sleep(4.5)
        assert self.dmcs.STATE_SCBD.get_archive_state() == 'DISABLE'
      
      
        msg = {}
        msg['MSG_TYPE'] = "ENABLE"
        msg['DEVICE'] = 'AR'
        msg['CMD_ID'] = '17718411'
        msg['ACK_ID'] = 'AR_11'
        msg['ACK_DELAY'] = 2
        time.sleep(4)
        print("AR ENABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        sleep(4.5)
        assert self.dmcs.STATE_SCBD.get_archive_state() == 'ENABLE'

        msg = {}
        msg['MSG_TYPE'] = "NEXT_VISIT"
        msg['VISIT_ID'] = 'V_1443'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['ACK_ID'] = 'NEW_VISIT_ACK_76'
        msg['BORE_SIGHT'] = "231,123786456342, -45.3457156906, FK5"
        time.sleep(4)
        print("Next Visit Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)

        sleep(0.5)
        assert self.dmcs.STATE_SCBD.get_current_visit() == 'V_1443'
      
        msg = {}
        msg['MSG_TYPE'] = "START_INTEGRATION"
        msg['IMAGE_ID'] = 'IMG_4276'
        msg['IMAGE_SRC'] = 'MAIN'
        msg['VISIT_ID'] = 'V_1443'
        msg['ACK_ID'] = 'START_INT_ACK_76'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['CCD_LIST'] = self.ccd_list
        time.sleep(4)
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
      
        time.sleep(5)

        print("Message Sender done")

    def clear_message_lists(self):
        self.ocs_consumer_msg_list = []
        self.ar_consumer_msg_list = []

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
   

    def on_ocs_message(self, ch, method, properties, body):
        self.ocs_consumer_msg_list.append(body)

 
    def on_ar_message(self, ch, method, properties, body):
        self.ar_consumer_msg_list.append(body)

