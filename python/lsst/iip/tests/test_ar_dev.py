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
import toolsmod
from toolsmod import get_timestamp
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from MessageAuthority import MessageAuthority
from const import *

from ArchiveDevice import *

logging.basicConfig(filename='logs/ARCHIVE_TEST.log', level=logging.INFO, format=LOG_FORMAT)

class TestArDev:
    ardev = ArchiveDevice('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test_ar.yaml')

    dmcs_pub_broker_url = None
    dmcs_publisher = None
    dmcs_consumer = None
    dmcs_consumer_msg_list = []

    ar_ctrl_pub_broker_url = None
    ar_ctrl_publisher = None
    ar_ctrl_consumer = None
    ar_ctrl_consumer_msg_list = []

    F1_pub_broker_url = None
    F1_publisher = None
    F1_consumer = None
    f1_consumer_msg_list = []

    F2_pub_broker_url = None
    F2_publisher = None
    F2_consumer = None
    f2_consumer_msg_list = []

    EXPECTED_AR_CTRL_MESSAGES = 1
    EXPECTED_DMCS_MESSAGES = 1
    EXPECTED_F1_MESSAGES = 1
    EXPECTED_F2_MESSAGES = 1

    ccd_list = [14,17,21.86]
    prp = toolsmod.prp


    def test_ardev(self):
        try:
            cdm = toolsmod.intake_yaml_file('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test_ar.yaml')
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
        print("Opening publisher with this URL string: %s" % dmcs_pub_broker_url)
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
        print("Opening publisher with this URL string: %s" % ar_ctrl_pub_broker_url)
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
        print("Opening publisher with this URL string: %s" % F1_pub_broker_url)
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
        print("Opening publisher with this URL string: %s" % F2_pub_broker_url)
        self.F2_publisher = SimplePublisher(F2_pub_broker_url, "YAML")
   
 
        # Must be done before consumer threads are started
        # This is used for verifying message structure
        self._msg_auth = MessageAuthority()

        self.dmcs_consumer = Consumer(dmcs_broker_url,'dmcs_ack_consume', 'thread-dmcs',
                                     self.on_dmcs_message,'YAML', None)
        self.dmcs_consumer.start()


        self.ar_ctrl_consumer = Consumer(ar_ctrl_broker_url,'archive_ctrl_consume', 'thread-ar-ctrl', 
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
        sleep(8)
        self.verify_ar_ctrl_messages()
        self.verify_dmcs_messages()
        self.verify_F1_messages()
        self.verify_F2_messages()

        print("Finished with AR tests.")
        #sys.exit(0)


    def send_messages(self):

        print("Starting send_messages")
        # Tests only an AR device
        
        self.EXPECTED_AR_CTRL_MESSAGES = 2
        self.EXPECTED_DMCS_MESSAGES = 4
        self.EXPECTED_F1_MESSAGES = 3
        self.EXPECTED_F2_MESSAGES = 3

        msg = {}
        msg['MSG_TYPE'] = "AR_NEW_SESSION"
        msg['SESSION_ID'] = 'SI_469976'
        msg['ACK_ID'] = 'NEW_SESSION_ACK_44221'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        time.sleep(2)
        print("New Session Message")
        self.dmcs_publisher.publish_message("ar_foreman_consume", msg)

        msg = {}
        msg['MSG_TYPE'] = "AR_NEXT_VISIT"
        msg['VISIT_ID'] = 'XX_28272' 
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'NEW_VISIT_ACK_76'
        msg['BORE_SIGHT'] = "231,123786456342, -45.3457156906, FK5"
        time.sleep(2)
        print("Next Visit Message")
        self.dmcs_publisher.publish_message("ar_foreman_consume", msg)
          
        msg = {}
        msg['MSG_TYPE'] = "AR_START_INTEGRATION"
        msg['JOB_NUM'] = '4xx72'
        msg['IMAGE_ID'] = 'IMG_444244'
        msg['VISIT_ID'] = 'V14494'
        msg['SESSION_ID'] = '4_14_7211511'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'AR_ACK_94671'
        msg['CCD_LIST'] = [4,14,16,17,29,35,36]
        time.sleep(2)
        print("AR Start Integration Message")
        self.dmcs_publisher.publish_message("ar_foreman_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "AR_READOUT"
        msg['JOB_NUM'] = '4xx72'
        msg['IMAGE_ID'] = 'IMG_444244'
        msg['VISIT_ID'] = 'V14494'
        msg['SESSION_ID'] = '4_14_7211511'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'ACK_44221'
        time.sleep(2)
        print("AR Readout Message")
        self.dmcs_publisher.publish_message("ar_foreman_consume", msg)

        time.sleep(9)
        print("Message Sender done")


    def verify_dmcs_messages(self):
        len_list = len(self.dmcs_consumer_msg_list)
        if len_list != self.EXPECTED_DMCS_MESSAGES:
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
        len_list = len(self.ar_ctrl_consumer_msg_list)
        if len_list != self.EXPECTED_AR_CTRL_MESSAGES:
            pytest.fail('AR CTRL simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_AR_CTRL_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.ar_ctrl_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                pytest.fail("The following message to the AR CTRL failed when compared with the sovereign example: %s" % msg)
        print("Messages to the AR CTRL pass verification.")
   

    def verify_F1_messages(self):
        len_list = len(self.f1_consumer_msg_list)
        if len_list != self.EXPECTED_F1_MESSAGES:
            pytest.fail('F1 simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_F1_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.f1_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                pytest.fail("The following message to F1 failed when compared with the sovereign example: %s" % msg)

        print("Messages to F1 pass verification.")
  
   
    def verify_F2_messages(self):
        len_list = len(self.f2_consumer_msg_list)
        if len_list != self.EXPECTED_F2_MESSAGES:
            pytest.fail('F2 simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_F2_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.f2_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                pytest.fail("The following message to F2 failed when compared with the sovereign example: %s" % msg)

        print("Messages to F2 pass verification.")
  
 
    def on_dmcs_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        self.dmcs_consumer_msg_list.append(body)


    def on_ar_ctrl_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        self.ar_ctrl_consumer_msg_list.append(body)
        if body['MSG_TYPE'] == 'NEW_ARCHIVE_ITEM':
            msg = {}
            msg['MSG_TYPE'] = 'NEW_ARCHIVE_ITEM_ACK'
            msg['COMPONENT'] = 'ARCHIVE_CTRL'
            msg['ACK_ID'] = body['ACK_ID']
            msg['ACK_BOOL'] = True
            msg['TARGET_DIR'] = '/dev/test/null' 
            self.ar_ctrl_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'AR_ITEMS_XFERD':
            msg = {}
            msg['MSG_TYPE'] = 'AR_ITEMS_XFERD_ACK'
            msg['COMPONENT'] = 'ARCHIVE_CTRL'
            msg['ACK_ID'] = body['ACK_ID']
            msg['ACK_BOOL'] = True
            msg['IMAGE_ID'] = body['IMAGE_ID']
            msg['RESULT_LIST'] = {}
            msg['RESULT_LIST']['CCD_LIST'] = []
            msg['RESULT_LIST']['RECEIPT_LIST'] = []
            CCD_LIST = []
            RECEIPT_LIST = []
            ccd_list = body['RESULT_LIST']['CCD_LIST']
            for ccd in ccd_list:
                CCD_LIST.append(ccd)  
                RECEIPT_LIST.append('x14_' + str(ccd))
            msg['RESULT_LIST']['CCD_LIST'] = CCD_LIST 
            msg['RESULT_LIST']['RECEIPT_LIST'] = RECEIPT_LIST 
            self.ar_ctrl_publisher.publish_message(body['REPLY_QUEUE'], msg)

        else:
            pytest.fail("The following unknown message was received by the Archive CTRL: %s" % body)

    def on_f1_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        self.f1_consumer_msg_list.append(body)
        if body['MSG_TYPE'] == 'AR_FWDR_HEALTH_CHECK':
            msg = {}
            msg['MSG_TYPE'] = 'AR_FWDR_HEALTH_CHECK_ACK'
            msg['COMPONENT'] = 'FORWARDER_1'
            msg['ACK_BOOL'] = True 
            msg['ACK_ID'] = body['ACK_ID']
            self.F1_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'AR_FWDR_XFER_PARAMS':
            msg = {}
            msg['MSG_TYPE'] = 'AR_FWDR_XFER_PARAMS_ACK'
            msg['COMPONENT'] = 'FORWARDER_1'
            msg['ACK_BOOL'] = True 
            msg['ACK_ID'] = body['ACK_ID']
            self.F1_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'AR_FWDR_READOUT':
            # Find message in message list for xfer_params
            xfer_msg = None
            for msg in self.f1_consumer_msg_list:
                if msg['MSG_TYPE'] == 'AR_FWDR_XFER_PARAMS':
                    xfer_msg = msg
                    break
            if xfer_msg == None:
                pytest.fail("The AR_FWDR_XFER_PARAMS message was not received before AR_FWDR_READOUT in F1")

            # use message to build response
            msg = {}
            msg['MSG_TYPE'] = 'AR_FWDR_READOUT_ACK'
            msg['COMPONENT'] = 'FORWARDER_1'
            msg['JOB_NUM'] = xfer_msg['JOB_NUM']
            msg['IMAGE_ID'] = xfer_msg['IMAGE_ID']
            msg['ACK_ID'] = body['ACK_ID']
            msg['ACK_BOOL'] = True
            msg['RESULT_LIST'] = {}
            msg['RESULT_LIST']['CCD_LIST'] = []
            msg['RESULT_LIST']['FILENAME_LIST'] = []
            msg['RESULT_LIST']['CHECKSUM_LIST'] = []
            CCD_LIST = []
            FILENAME_LIST = []
            CHECKSUM_LIST = []
            target_dir = xfer_msg['TARGET_DIR']
            ccd_list = xfer_msg['XFER_PARAMS']['CCD_LIST']
            for ccd in ccd_list:
                CCD_LIST.append(ccd)
                FILENAME_LIST.append(target_dir + str(ccd))
                CHECKSUM_LIST.append('XXXXFFFF4444$$$$')
            msg['RESULT_LIST']['CCD_LIST'] = CCD_LIST
            msg['RESULT_LIST']['FILENAME_LIST'] = FILENAME_LIST
            msg['RESULT_LIST']['CHECKSUM_LIST'] = CHECKSUM_LIST
            self.F1_publisher.publish_message(body['REPLY_QUEUE'], msg)

        else:
            pytest.fail("The following unknown message was received by FWDR F1: %s" % body)


    def on_f2_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        self.f2_consumer_msg_list.append(body)
        if body['MSG_TYPE'] == 'AR_FWDR_HEALTH_CHECK':
            msg = {}
            msg['MSG_TYPE'] = 'AR_FWDR_HEALTH_CHECK_ACK'
            msg['COMPONENT'] = 'FORWARDER_2'
            msg['ACK_BOOL'] = True 
            msg['ACK_ID'] = body['ACK_ID']
            self.F2_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'AR_FWDR_XFER_PARAMS':
            msg = {}
            msg['MSG_TYPE'] = 'AR_FWDR_XFER_PARAMS_ACK'
            msg['COMPONENT'] = 'FORWARDER_2'
            msg['ACK_BOOL'] = True 
            msg['ACK_ID'] = body['ACK_ID']
            self.F2_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'AR_FWDR_READOUT':
            # Find message in message list for xfer_params
            xfer_msg = None
            for msg in self.f2_consumer_msg_list:
                if msg['MSG_TYPE'] == 'AR_FWDR_XFER_PARAMS':
                    xfer_msg = msg
                    break
            if xfer_msg == None:
                pytest.fail("The AR_FWDR_XFER_PARAMS message was not received before AR_FWDR_READOUT in F2")

            # use message to build response
            msg = {}
            msg['MSG_TYPE'] = 'AR_FWDR_READOUT_ACK'
            msg['COMPONENT'] = 'FORWARDER_2'
            msg['JOB_NUM'] = xfer_msg['JOB_NUM']
            msg['IMAGE_ID'] = xfer_msg['IMAGE_ID']
            msg['ACK_ID'] = body['ACK_ID']
            msg['ACK_BOOL'] = True
            msg['RESULT_LIST'] = {}
            msg['RESULT_LIST']['CCD_LIST'] = []
            msg['RESULT_LIST']['FILENAME_LIST'] = []
            msg['RESULT_LIST']['CHECKSUM_LIST'] = []
            CCD_LIST = []
            FILENAME_LIST = []
            CHECKSUM_LIST = []
            target_dir = xfer_msg['TARGET_DIR']
            ccd_list = xfer_msg['XFER_PARAMS']['CCD_LIST']
            for ccd in ccd_list:
                CCD_LIST.append(ccd)
                FILENAME_LIST.append(target_dir + str(ccd))
                CHECKSUM_LIST.append('XXXXFFFF4444$$$$')
            msg['RESULT_LIST']['CCD_LIST'] = CCD_LIST
            msg['RESULT_LIST']['FILENAME_LIST'] = FILENAME_LIST
            msg['RESULT_LIST']['CHECKSUM_LIST'] = CHECKSUM_LIST
            print("----------------------\nAt end of  F2 Message AR_FWDR_READOUT...")
            print("%s" % get_timestamp())
            print("------------------------------------\n\n")
            self.F2_publisher.publish_message(body['REPLY_QUEUE'], msg)

        else:
            pytest.fail("The following unknown message was received by FWDR F2: %s" % body)


