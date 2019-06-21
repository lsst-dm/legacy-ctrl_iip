###############################################
# See README_PYTESTS for testing instructions #
###############################################

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

logging.basicConfig(filename='logs/DMCS_TEST.log', level=logging.INFO, format=LOG_FORMAT)

@pytest.fixture(scope='session')
def Dmcs(request):
    dmcs = DMCS('tests/yaml/L1SystemCfg_Test.yaml')
    request.addfinalizer(dmcs.shutdown)
    return dmcs


class TestDMCS_AR_PP:

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
    DP = toolsmod.DP  # Debug Print


    
    def test_dmcs(self, Dmcs):
        self.dmcs = Dmcs
        try:
            cdm = toolsmod.intake_yaml_file('tests/yaml/L1SystemCfg_Test.yaml')
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
                                     self.on_ocs_message,'YAML')
        self.ocs_consumer.start()


        self.ar_consumer = Consumer(ar_broker_url,'ar_foreman_consume', 'thread-ar',
                                    self.on_ar_message,'YAML')
        self.ar_consumer.start()


        self.pp_consumer = Consumer(pp_broker_url,'pp_foreman_consume', 'thread-pp',
                                    self.on_pp_message,'YAML')
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
        self.ocs_consumer.stop()
        self.ocs_consumer.join()
        self.ar_consumer.stop()
        self.ar_consumer.join()
        self.pp_consumer.stop()
        self.pp_consumer.join()
        print("Finished with DMCS AR and PP tests.")


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

