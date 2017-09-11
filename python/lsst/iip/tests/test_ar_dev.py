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

from ArchiveDevice import *

logging.basicConfig(filename='logs/DMCS_TEST.log', level=logging.INFO, format=LOG_FORMAT)

class TestArDev:
    ardev = ArchiveDevice('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test.yaml')

    dmcs_pub_broker_url = None
    dmcs_publisher = None
    dmcs_consumer = None
    dmcs_consumer_msg_list = []

    ar_ctrl_pub_broker_url = None
    ar_ctrl_publisher = None
    ar_ctrl_consumer = None
    ar_ctrl_consumer_msg_list = []

    EXPECTED_AR_CTRL_MESSAGES = 1
    EXPECTED_DMCS_MESSAGES = 1
    EXPECTED_F1_MESSAGES = 1
    EXPECTED_F2_MESSAGES = 1

    ccd_list = [14,17,21.86]
    prp = toolsmod.prp


    def test_ardev(self):
        try:
            cdm = toolsmod.intake_yaml_file('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test.yaml')
        except IOError as e:
            trace = traceback.print_exc()
            emsg = "Unable to find CFG Yaml file %s\n" % self._config_file
            print(emsg + trace)
            sys.exit(101)
    
        broker_addr = cdm[ROOT]['BASE_BROKER_ADDR']
    
        dmcs_name = cdm[ROOT]['DMCS_BROKER_NAME']
        dmcs_passwd = cdm[ROOT]['DMCS_BROKER_PASSWD']
        dmcs_pub_name = cdm[ROOT]['DMCS_BROKER_PUB_NAME']
        dmcs_pub_passwd = cdm[ROOT]['DMCS_BROKER_PUB_PASSWD']
        dmcs_broker_url = "amqp://" + dmcs_name + ":" + \
                                 dmcs_passwd + "@" + \
                                 broker_addr
        dmcs_pub_broker_url = "amqp://" + dmcs_pub_name + ":" + \
                                 dmcs_pub_passwd + "@" + \
                                 broker_addr
        self.dmcs_publisher = SimplePublisher(dmcs_pub_broker_url, "YAML")
    
        ar_ctrl_name = cdm[ROOT]['ARCHIVE_BROKER_NAME']
        ar_ctrl_passwd = cdm[ROOT]['ARCHIVE_BROKER_PASSWD']
        ar_ctrl_pub_name = cdm[ROOT]['ARCHIVE_BROKER_PUB_NAME']
        ar_ctrl_pub_passwd = cdm[ROOT]['ARCHIVE_BROKER_PUB_PASSWD']
        ar_ctrl_broker_url = "amqp://" + ar_ctrl_name + ":" + \
                                ar_ctrl_passwd + "@" + \
                                broker_addr
        ar_ctrl_pub_broker_url = "amqp://" + ar_ctrl_pub_name + ":" + \
                                    ar_ctrl_pub_passwd + "@" + \
                                    broker_addr
        self.ar_ctrl_publisher = SimplePublisher(ar_ctrl_pub_broker_url, "YAML")
    
        F1_name = 'F1'
        F1_passwd = 'F1'
        F1_pub_name = 'F1_PUB'
        F1_pub_passwd = 'F1_PUB'
        F1_broker_url = "amqp://" + F1_name + ":" + \
                                F1_passwd + "@" + \
                                broker_addr
        F1_pub_broker_url = "amqp://" + F1_pub_name + ":" + \
                                    F1_pub_passwd + "@" + \
                                    broker_addr
        self.F1_publisher = SimplePublisher(F1_pub_broker_url, "YAML")
   
        F2_name = 'F2'
        F2_passwd = 'F2'
        F2_pub_name = 'F2_PUB'
        F2_pub_passwd = 'F2_PUB'
        F2_broker_url = "amqp://" + F2_name + ":" + \
                                F2_passwd + "@" + \
                                broker_addr
        F2_pub_broker_url = "amqp://" + F2_pub_name + ":" + \
                                    F2_pub_passwd + "@" + \
                                    broker_addr
        self.F2_publisher = SimplePublisher(F2_pub_broker_url, "YAML")
   
 
        # Must be done before consumer threads are started
        # This is used for verifying message structure
        self._msg_auth = MessageAuthority()

        self.dmcs_consumer = Consumer(self.dmcs, dmcs_broker_url,'dmcs_ack_consume', 'thread-dmcs',
                                     self.on_dmcs_message,'YAML', None)
        self.dmcs_consumer.start()


        self.ar_ctrl_consumer = Consumer(ar_ctrl_broker_url,'ar_foreman_consume', 'thread-ar-ctrl', 
                                    self.on_ar_ctrl_message,'YAML', None)
        self.ar_ctrl_consumer.start()

        self.F1_consumer = Consumer(F1_broker_url,'f1_consume', 'thread-f1', 
                                    self.on_f1_message,'YAML', None)
        self.F1_consumer.start()

        self.F2_consumer = Consumer(F2_broker_url,'f2_consume', 'thread-f2', 
                                    self.on_f2_message,'YAML', None)
        self.F2_consumer.start()

        sleep(3)
        print("Test Setup Complete. Commencing Messages...")

        self.send_messages()
        self.verify_dmcs_messages()
        self.verify_ar_ctrl_messages()
        self.verify_F1_messages()
        self.verify_F2_messages()

        sleep(2)
        print("Finished with AR tests.")
        #sys.exit(0)


    def send_messages(self):

        print("Starting send_messages")
        # Tests only an AR device
        
        self.clear_message_lists()

        self.EXPECTED_OCS_MESSAGES = 6
        self.EXPECTED_AR_MESSAGES = 6

        msg = {}
        msg['MSG_TYPE'] = "STANDBY"
        msg['DEVICE'] = 'AR'
        msg['CFG_KEY'] = "2C16"
        msg['ACK_ID'] = 'AR_4'
        msg['ACK_DELAY'] = 2
        time.sleep(2)
        print("AR STANDBY")
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
        time.sleep(2)
        print("AR DISABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)

        sleep(0.5)
        assert self.dmcs.STATE_SCBD.get_archive_state() == 'DISABLE'
      
      
        msg = {}
        msg['MSG_TYPE'] = "ENABLE"
        msg['DEVICE'] = 'AR'
        msg['ACK_ID'] = 'AR_11'
        msg['ACK_DELAY'] = 2
        time.sleep(2)
        print("AR ENABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        sleep(0.5)
        assert self.dmcs.STATE_SCBD.get_archive_state() == 'ENABLE'

        msg = {}
        msg['MSG_TYPE'] = "NEXT_VISIT"
        msg['VISIT_ID'] = 'V_1443'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['ACK_ID'] = 'NEW_VISIT_ACK_76'
        msg['BORE_SIGHT'] = "231,123786456342, -45.3457156906, FK5"
        time.sleep(2)
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
        time.sleep(2)
        print("Start Integration Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "READOUT"
        msg['VISIT_ID'] = 'V_1443'
        msg['IMAGE_ID'] = 'IMG_4276'
        msg['IMAGE_SRC'] = 'MAIN'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['ACK_ID'] = 'READOUT_ACK_77'
        time.sleep(2)
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
        time.sleep(2)
        print("Start Integration Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "READOUT"
        msg['VISIT_ID'] = 'V_1443'
        msg['IMAGE_ID'] = 'IMG_4277'
        msg['IMAGE_SRC'] = 'MAIN'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['ACK_ID'] = 'READOUT_ACK_79'
        time.sleep(2)
        print("READOUT Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        time.sleep(2)

        print("Message Sender done")

    def clear_message_lists(self):
        self.dmcs_consumer_msg_list = []
        self.ar_ctrl_consumer_msg_list = []

    def verify_dmcs_messages(self):
        print("Messages received by verify_dmcs_messages:")
        self.prp.pprint(self.dmcs_consumer_msg_list)
        len_list = len(self.dmcs_consumer_msg_list)
        if len_list != self.EXPECTED_OCS_MESSAGES:
            print("Messages received by verify_dmcs_messages:")
            self.prp.pprint(self.dmcs_consumer_msg_list)
            pytest.fail('DMCS simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_DMCS_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.dmcs_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                pytest.fail("The following DMCS Bridge response message failed when compared with the sovereign example: %s" % msg)
        print("Responses to DMCS Bridge pass verification.")
   

    def verify_ar_ctrl_messages(self):
        print("Messages received by verify_ar_ctrl_messages:")
        self.prp.pprint(self.ar_ctrl_consumer_msg_list)
        len_list = len(self.ar_ctrl_consumer_msg_list)
        if len_list != self.EXPECTED_AR_CTRL_MESSAGES:
            print("Messages received by verify_ar_ctrl_messages:")
            self.prp.pprint(self.ar_ctrl_consumer_msg_list)
            pytest.fail('AR CTRL simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_AR_CTRL_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.ar_ctrl_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                pytest.fail("The following message to the AR CTRL failed when compared with the sovereign example: %s" % msg)
        print("Messages to the AR CTRL pass verification.")
   

    def on_dmcs_message(self, ch, method, properties, body):
        self.dmcs_consumer_msg_list.append(body)

 
    def on_ar_ctrl_message(self, ch, method, properties, body):
        self.ar_ctrl_consumer_msg_list.append(body)

