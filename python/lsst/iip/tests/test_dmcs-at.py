###############################################
# See README_PYTESTS for testing instructions #
###############################################

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

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename='logs/DMCS_TEST.log', level=logging.INFO, format=LOG_FORMAT)

@pytest.fixture(scope='session')
def Dmcs(request):
    dmcs = DMCS('tests/yaml/L1SystemCfg_Test.yaml')
    request.addfinalizer(dmcs.shutdown)
    return dmcs

class TestDMCS_AT:

    ocs_pub_broker_url = None
    ocs_publisher = None
    ocs_consumer = None
    ocs_consumer_msg_list = []

    at_pub_broker_url = None
    at_publisher = None
    at_consumer = None
    at_consumer_msg_list = []

    EXPECTED_AT_MESSAGES = 1
    EXPECTED_OCS_MESSAGES = 1

    prp = toolsmod.prp
    #DP = toolsmod.DP  #Debug print
    DP = True  #Debug print


    def test_dmcs(self, Dmcs):
        self.dmcs = Dmcs
        #logging.warning("Logging is Working!")
        LOGGER.critical("LOGGING is Working!")
        #self.LOGGER.info("self Logging is Working!")
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
        self.ocs_pub_broker_url = "amqp://" + ocs_pub_name + ":" + \
                                 ocs_pub_passwd + "@" + \
                                 broker_addr
        self.ocs_publisher = SimplePublisher(self.ocs_pub_broker_url, "YAML")
    
        at_name = cdm[ROOT]['AUX_BROKER_NAME']
        at_passwd = cdm[ROOT]['AUX_BROKER_PASSWD']
        at_pub_name = cdm[ROOT]['AUX_BROKER_PUB_NAME']
        at_pub_passwd = cdm[ROOT]['AUX_BROKER_PUB_PASSWD']
        at_broker_url = "amqp://" + at_name + ":" + \
                                at_passwd + "@" + \
                                broker_addr
        self.at_pub_broker_url = "amqp://" + at_pub_name + ":" + \
                                    at_pub_passwd + "@" + \
                                    broker_addr
        self.at_publisher = SimplePublisher(self.at_pub_broker_url, "YAML")
    
        # Must be done before consumer threads are started
        # This is used for verifying message structure
        self._msg_auth = MessageAuthority()

        self.ocs_consumer = Consumer(ocs_broker_url,'dmcs_ocs_publish', 'thread-ocs',
                                     self.on_ocs_message,'YAML')
        self.ocs_consumer.start()

        self.at_consumer = Consumer(at_broker_url,'at_foreman_consume', 'thread-at', 
                                    self.on_at_message,'YAML')
        self.at_consumer.start()

        sleep(3)
        if self.DP:
            print("Test Setup Complete. Commencing Messages...")

        self.send_messages()
        sleep(3)
        self.verify_ocs_messages()
        sleep(3)
        self.verify_at_messages()

        sleep(2)
        self.ocs_consumer.stop()
        self.ocs_consumer.join()
        self.at_consumer.stop()
        self.at_consumer.join()
        if self.DP:
            print("Finished with DMCS AT tests.")
        


    def send_messages(self):

        if self.DP:
            print("Starting send_messages")
        # Tests only an AT device
        
        self.clear_message_lists()

        self.EXPECTED_OCS_MESSAGES = 6
        self.EXPECTED_AT_MESSAGES = 4

        msg = {}
        msg['MSG_TYPE'] = "STANDBY"
        msg['DEVICE'] = 'AT'
        msg['CMD_ID'] = '17718411'
        msg['CFG_KEY'] = "2C16"
        msg['ACK_ID'] = 'AT_4'
        msg['ACK_DELAY'] = 2
        time.sleep(2)
        if self.DP:
            print("Sending AT STANDBY")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "DISABLE"
        msg['DEVICE'] = 'AT'
        msg['CMD_ID'] = '17718411'
        msg['ACK_ID'] = 'AT_6'
        msg['ACK_DELAY'] = 2
        time.sleep(2)
        if self.DP:
            print("Sending AT DISABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)

        sleep(2.0)
        # Make sertain scoreboard values are being set
        if self.DP:
            print("Checking State Scoreboard entries.")
        #assert self.dmcs.STATE_SCBD.get_auxdev_state() == 'DISABLE'
        assert self.dmcs.STATE_SCBD.get_auxtel_state() == 'DISABLE'
      
      
        msg = {}
        msg['MSG_TYPE'] = "ENABLE"
        msg['DEVICE'] = 'AT'
        msg['CMD_ID'] = '17718411'
        msg['ACK_ID'] = 'AT_11'
        msg['ACK_DELAY'] = 2
        time.sleep(4)
        if self.DP:
            print("Sending AT ENABLE")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
      
        sleep(2.0)
        #assert self.dmcs.STATE_SCBD.get_auxdev_state() == 'ENABLE'
        assert self.dmcs.STATE_SCBD.get_auxtel_state() == 'ENABLE'

        msg = {}
        msg['MSG_TYPE'] = "DMCS_AT_START_INTEGRATION"
        msg['IMAGE_ID'] = 'IMG_4280'
        msg['IMAGE_INDEX'] = 2
        msg['IMAGE_SEQUENCE_NAME'] = 'XX_seq'
        msg['IMAGES_IN_SEQUENCE'] = 8
        time.sleep(5)
        if self.DP:
            print("Sending Start Integration Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
     
        msg = {}
        msg['MSG_TYPE'] = "DMCS_AT_END_READOUT"
        msg['IMAGE_ID'] = 'IMG_4280'
        msg['IMAGE_INDEX'] = 2
        msg['IMAGE_SEQUENCE_NAME'] = 'XX_seq'
        msg['IMAGES_IN_SEQUENCE'] = 8
        time.sleep(5)
        if self.DP:
            print("Sending READOUT Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
     
        msg = {}
        msg['MSG_TYPE'] = "DMCS_AT_HEADER_READY"
        msg['IMAGE_ID'] = 'IMG_4280'
        msg['FILENAME'] = "/mnt/headers/IMG_4277.header"
        msg['ACK_ID'] = 'DMCS_END_READOUT_ACK_82'
        time.sleep(5)
        if self.DP:
            print("Sending HEADER_READY Message")
        self.ocs_publisher.publish_message("ocs_dmcs_consume", msg)
     
     
        time.sleep(5)

        if self.DP:
            print("Message Sender done")

    def clear_message_lists(self):
        self.ocs_consumer_msg_list = []
        self.at_consumer_msg_list = []

    def verify_ocs_messages(self):
        if self.DP:
            print("Messages received by verify_ocs_messages:")
            self.prp.pprint(self.ocs_consumer_msg_list)
        len_list = len(self.ocs_consumer_msg_list)
        if len_list != self.EXPECTED_OCS_MESSAGES:
            if self.DP:
                print("Incorrect number of messages received by OCS ACK Consumer.")
                print("Messages received by verify_ocs_messages:")
                self.prp.pprint(self.ocs_consumer_msg_list)
            pytest.fail('OCS simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_OCS_MESSAGES, len_list))

        # Now check num keys in each message and check for key errors
        for i in range(0, len_list):
            msg = self.ocs_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                pytest.fail("The following OCS Bridge response message failed when compared with the sovereign example: %s" % msg)
        if self.DP:
            print("Responses to OCS Bridge pass verification.")
   

    def verify_at_messages(self):
        if self.DP:
            print("Messages received by verify_at_messages:")
            self.prp.pprint(self.at_consumer_msg_list)
        len_list = len(self.at_consumer_msg_list)
        if self.DP:
            print("The number of messages the AT received is %s" % len_list)
        if len_list != self.EXPECTED_AT_MESSAGES:
            if self.DP:
                print("Messages received by verify_at_messages:")
                self.prp.pprint(self.at_consumer_msg_list)
            pytest.fail('AT simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_AT_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.at_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                if self.DP:
                    print("The following message to the AT failed when compared with " \
                          "the sovereign example: %s" % msg)
                pytest.fail("The following message to the AT failed when compared with " \
                            "the sovereign example: %s" % msg)

        if self.DP:
            print("Messages to the AT pass verification.")
   

    def on_ocs_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        if self.DP:
            print("In test_dmcs-at - incoming on_ocs_message")
            self.prp.pprint(body)
            print("\n----------------------\n\n")
        self.ocs_consumer_msg_list.append(body)

 
    def on_at_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        if self.DP:
            print("In test_dmcs-at - incoming on_at_message")
            self.prp.pprint(body)
            print("\n----------------------\n\n")
        self.at_consumer_msg_list.append(body)

