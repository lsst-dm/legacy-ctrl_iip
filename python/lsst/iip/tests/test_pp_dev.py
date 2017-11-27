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
from copy import deepcopy
import logging
sys.path.insert(1, '../iip')
sys.path.insert(1, '../')
import DMCS
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from MessageAuthority import MessageAuthority
from const import *
import toolsmod
from PromptProcessDevice import *

logging.basicConfig(filename='logs/PP_AR_TEST.log', level=logging.INFO, format=LOG_FORMAT)

@pytest.fixture(scope='session')
def Ppdev(request):
    ppdev = PromptProcessDevice('./tests/yaml/L1SystemCfg_Test_pp.yaml')
    request.addfinalizer(ppdev.shutdown)
    return ppdev

class TestPpDev:

    dmcs_pub_broker_url = None
    dmcs_publisher = None
    dmcs_consumer = None
    dmcs_consumer_msg_list = []

    ncsa_pub_broker_url = None
    ncsa_publisher = None
    ncsa_ctrl_consumer = None
    ncsa_consumer_msg_list = []

    F1_pub_broker_url = None
    F1_publisher = None
    F1_consumer = None
    f1_consumer_msg_list = []

    F2_pub_broker_url = None
    F2_publisher = None
    F2_consumer = None
    f2_consumer_msg_list = []

    EXPECTED_NCSA_MESSAGES = 1
    EXPECTED_DMCS_MESSAGES = 1
    EXPECTED_F1_MESSAGES = 1
    EXPECTED_F2_MESSAGES = 1

    ccd_list = [14,17,21,86]
    prp = toolsmod.prp # pretty printing
    DP = toolsmod.DP  # Debug printing either True of False...set here to override this file only


    def test_ppdev(self, Ppdev):
        self.ppdev = Ppdev
        try:
            cdm = toolsmod.intake_yaml_file('./tests/yaml/L1SystemCfg_Test.yaml')
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
    
        ncsa_name = cdm[ROOT]['NCSA_BROKER_NAME']
        ncsa_passwd = cdm[ROOT]['NCSA_BROKER_PASSWD']
        ncsa_pub_name = cdm[ROOT]['NCSA_BROKER_PUB_NAME']
        ncsa_pub_passwd = cdm[ROOT]['NCSA_BROKER_PUB_PASSWD']
        ncsa_broker_url = "amqp://" + ncsa_name + ":" + \
                                ncsa_passwd + "@" + \
                                broker_addr
        ncsa_pub_broker_url = "amqp://" + ncsa_pub_name + ":" + \
                                    ncsa_pub_passwd + "@" + \
                                    broker_addr
        self.ncsa_publisher = SimplePublisher(ncsa_pub_broker_url, "YAML")
    
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
        self.f1_publisher = SimplePublisher(F1_pub_broker_url, "YAML")
   
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
        self.f2_publisher = SimplePublisher(F2_pub_broker_url, "YAML")
   
 
        # Must be done before consumer threads are started
        # This is used for verifying message structure
        self._msg_auth = MessageAuthority()

        self.dmcs_consumer = Consumer(dmcs_broker_url,'dmcs_ack_consume', 'thread-dmcs',
                                     self.on_dmcs_message,'YAML')
        self.dmcs_consumer.start()


        self.ncsa_consumer = Consumer(ncsa_broker_url,'ncsa_consume', 'thread-ncsa', 
                                    self.on_ncsa_message,'YAML')
        self.ncsa_consumer.start()


        self.F1_consumer = Consumer(F1_broker_url,'f1_consume', 'thread-f1', 
                                    self.on_f1_message,'YAML')
        self.F1_consumer.start()


        self.F2_consumer = Consumer(F2_broker_url,'f2_consume', 'thread-f2', 
                                    self.on_f2_message,'YAML')
        self.F2_consumer.start()

        sleep(3)
        if self.DP:
            print("Test Setup Complete. Commencing Messages...")

        self.send_messages()
        sleep(6)
        self.verify_ncsa_messages()
        self.verify_F2_messages()
        self.verify_F1_messages()
        self.verify_dmcs_messages()

        sleep(2)
        self.dmcs_consumer.stop()
        self.dmcs_consumer.join()
        self.ncsa_consumer.stop()
        self.ncsa_consumer.join()
        self.F1_consumer.stop()
        self.F1_consumer.join()
        self.F2_consumer.stop()
        self.F2_consumer.join()
        if self.DP:
            print("Finished with PP tests.")


    def send_messages(self):

        if self.DP:
            print("Starting send_messages")
        # Tests only an AR device
        
        # self.clear_message_lists()

        self.EXPECTED_NCSA_MESSAGES = 3
        self.EXPECTED_DMCS_MESSAGES = 4
        self.EXPECTED_F1_MESSAGES = 3
        self.EXPECTED_F2_MESSAGES = 3

        msg = {}
        msg['MSG_TYPE'] = "PP_NEW_SESSION"
        msg['SESSION_ID'] = 'SI_469976'
        msg['ACK_ID'] = 'NEW_SESSION_ACK_44221'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        time.sleep(3)
        if self.DP:
            print("New Session Message")
        self.dmcs_publisher.publish_message("pp_foreman_consume", msg)

        msg = {}
        msg['MSG_TYPE'] = "PP_NEXT_VISIT"
        msg['VISIT_ID'] = 'XX_28272' 
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'NEW_VISIT_ACK_76'
        msg['BORE_SIGHT'] = "231,123786456342, -45.3457156906, FK5"
        time.sleep(2)
        if self.DP:
            print("Next Visit Message")
        self.dmcs_publisher.publish_message("pp_foreman_consume", msg)
          
        msg = {}
        msg['MSG_TYPE'] = "PP_START_INTEGRATION"
        msg['JOB_NUM'] = '4xx72'
        msg['IMAGE_ID'] = 'IMG_444244'
        msg['VISIT_ID'] = 'V14494'
        msg['SESSION_ID'] = '4_14_7211511'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'PP_ACK_94671'
        msg['CCD_LIST'] = [4,14,16,17,29,35,36]
        time.sleep(4)
        if self.DP:
            print("PP_START_INTEGRATION Message")
        self.dmcs_publisher.publish_message("pp_foreman_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "PP_READOUT"
        msg['JOB_NUM'] = '4xx72'
        msg['IMAGE_ID'] = 'IMG_444244'
        msg['VISIT_ID'] = 'V14494'
        msg['SESSION_ID'] = '4_14_7211511'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'PP_READOUT_ACK_44221'
        time.sleep(4)
        if self.DP:
            print("PP_READOUT Message")
        self.dmcs_publisher.publish_message("pp_foreman_consume", msg)

        time.sleep(2)

        if self.DP:
            print("Message Sender done")


    def verify_dmcs_messages(self):
        if self.DP:
            print("Messages received by verify_dmcs_messages:")
            self.prp.pprint(self.dmcs_consumer_msg_list)
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
   

    def verify_ncsa_messages(self):
        if self.DP:
            print("Messages received by verify_ncsa_messages:")
            self.prp.pprint(self.ncsa_consumer_msg_list)
        len_list = len(self.ncsa_consumer_msg_list)
        if len_list != self.EXPECTED_NCSA_MESSAGES:
            pytest.fail('NCSA simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_NCSA_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.ncsa_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                pytest.fail("The following message to the NCSA Foreman failed when compared with the sovereign example: %s" % msg)
        print("Messages to the NCSA Foreman pass verification.")
   

    def verify_F1_messages(self):
        if self.DP:
            print("Messages received by verify_F1_messages:")
            self.prp.pprint(self.f1_consumer_msg_list)
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
            else:
                print("Messages to F1 pass verification.")
  
   
    def verify_F2_messages(self):
        if self.DP:
            print("Messages received by verify_F2_messages:")
            self.prp.pprint(self.f2_consumer_msg_list)
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
            else:
                print("Messages to F2 pass verification.")
  
 
    def on_dmcs_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        if self.DP:
            print("In test_pp_dev - incoming on_dmcs_message")
            self.prp.pprint(body)
            print("\n----------------------\n\n")
        self.dmcs_consumer_msg_list.append(body)

    def on_ncsa_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        if self.DP:
            print("In test_pp_dev - incoming on_ncsa_message")
            self.prp.pprint(body)
            print("\n----------------------\n\n")
        self.ncsa_consumer_msg_list.append(body)

        if body['MSG_TYPE'] == 'NCSA_NEW_SESSION':
            msg = {}
            msg['MSG_TYPE'] = 'NCSA_NEW_SESSION_ACK'
            msg['COMPONENT'] = 'NCSA_FOREMAN'
            msg['ACK_ID'] = body['ACK_ID']
            msg['ACK_BOOL'] = True
            self.ncsa_publisher.publish_message(body['REPLY_QUEUE'], msg)
            return

        if body['MSG_TYPE'] == 'NCSA_NEXT_VISIT':
            msg = {}
            msg['MSG_TYPE'] = 'NCSA_NEXT_VISIT_ACK'
            msg['COMPONENT'] = 'NCSA_FOREMAN'
            msg['ACK_ID'] = body['ACK_ID']
            msg['ACK_BOOL'] = True
            self.ncsa_publisher.publish_message(body['REPLY_QUEUE'], msg)
            return

        if body['MSG_TYPE'] == 'NCSA_START_INTEGRATION':
            msg = {}
            msg['ACK_ID'] = body['ACK_ID']
            msg['MSG_TYPE'] = 'NCSA_START_INTEGRATION_ACK'
            msg['COMPONENT'] = 'NCSA_FOREMAN'
            fwdrs = deepcopy(body['FORWARDERS'])
            fwdr_list = fwdrs['FORWARDER_LIST']
            ccd_list = fwdrs['CCD_LIST']
            i = 1
            msg['PAIRS'] = []  # This will be a list of dictionaries
            for i in range(0,len(fwdr_list)):
                fwdr = fwdr_list[i]
                dist = {}
                pair = {}
                dist['FQN'] = "Distributor_" + str(i)
                dist['NAME'] = "D" + str(i)
                dist['HOSTNAME'] = "D" + str(i)
                dist['TARGET_DIR'] = "/dev/null"
                dist['IP_ADDR'] = "141.142.237.16" + str(i)
                pair['FORWARDER'] = fwdr_list[i]
                pair['CCD_LIST'] = ccd_list[i]  #Get the list at index position i in ccd_list
                pair['DISTRIBUTOR'] = dist
                msg['PAIRS'].append(deepcopy(pair))
        
            msg['ACK_BOOL'] = True
            msg['JOB_NUM'] = body['JOB_NUM']
            msg['IMAGE_ID'] = body['IMAGE_ID']
            msg['VISIT_ID'] = body['VISIT_ID']
            msg['SESSION_ID'] = body['SESSION_ID']
            self.ncsa_publisher.publish_message(body['REPLY_QUEUE'], msg)
            return

        if body['MSG_TYPE'] == 'NCSA_READOUT':
            # Find earlier Start Int message
            st_int_msg = None
            for msg in self.ncsa_consumer_msg_list:
                if msg['MSG_TYPE'] == 'NCSA_START_INTEGRATION':
                    st_int_msg = msg
                    break
            if st_int_msg == None:
                pytest.fail("The NCSA_START_INTEGRATION message wasn't received before NCSA_READOUT in on_ncsa_msg")

            # Now build response with previous message
            msg = {}
            msg['MSG_TYPE'] = 'NCSA_READOUT_ACK'
            msg['JOB_NUM'] = body['JOB_NUM']
            msg['IMAGE_ID'] = body['IMAGE_ID']
            msg['VISIT_ID'] = body['VISIT_ID']
            msg['SESSION_ID'] = body['SESSION_ID']
            msg['COMPONENT'] = 'NCSA_FOREMAN'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            #msg['RESULT_LIST']['FORWARDER_LIST'] = st_int_msg['FORWARDERS']['FORWARDER_LIST']
            ccd_list = st_int_msg['FORWARDERS']['CCD_LIST']
            receipt_list = []
            for i in range(0, len(ccd_list)):
                receipt_list.append('Rec_x447_' + str(i))
            msg['RESULT_LIST'] = {}
            msg['RESULT_LIST']['RECEIPT_LIST'] = receipt_list
            msg['RESULT_LIST']['CCD_LIST'] = list(ccd_list)

            #sleep(2) #Give FWDRs time to respond with ack first
            self.ncsa_publisher.publish_message(body['REPLY_QUEUE'], msg)
     

    def on_f1_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        if self.DP:
            print("In test_pp_dev - incoming on_f1_message")
            self.prp.pprint(body)
            print("\n----------------------\n\n")
        self.f1_consumer_msg_list.append(body)

        if body['MSG_TYPE'] == 'PP_FWDR_HEALTH_CHECK':
            msg = {}
            msg['MSG_TYPE'] = 'PP_FWDR_HEALTH_CHECK_ACK'
            msg['COMPONENT'] = 'FORWARDER_1'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            self.f1_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'PP_FWDR_XFER_PARAMS':
            msg = {}
            msg['MSG_TYPE'] = 'PP_FWDR_XFER_PARAMS_ACK'
            msg['COMPONENT'] = 'FORWARDER_1'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            self.f1_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'PP_FWDR_READOUT':
            # Find message in message list for xfer_params
            xfer_msg = None
            for msg in self.f1_consumer_msg_list:
                if msg['MSG_TYPE'] == 'PP_FWDR_XFER_PARAMS':
                    xfer_msg = msg
                    break
            if xfer_msg == None:
                pytest.fail("The PP_FWDR_XFER_PARAMS message was not received before PP_FWDR_READOUT in F1")

            # use message to build response
            msg = {}
            msg['MSG_TYPE'] = 'PP_FWDR_READOUT_ACK'
            msg['COMPONENT'] = 'FORWARDER_1'
            msg['JOB_NUM'] = xfer_msg['JOB_NUM']
            msg['IMAGE_ID'] = xfer_msg['IMAGE_ID']
            msg['ACK_ID'] = body['ACK_ID']
            msg['ACK_BOOL'] = True
            msg['RESULT_LIST'] = {}
            msg['RESULT_LIST']['CCD_LIST'] = []
            msg['RESULT_LIST']['RECEIPT_LIST'] = []
            ccd_list = xfer_msg['XFER_PARAMS']['CCD_LIST']
            receipt_list = []
            for i in range(0, len(ccd_list)):
                receipt_list.append('F1_Rec_x477_' + str(i))
            msg['RESULT_LIST']['RECEIPT_LIST'] = receipt_list
            msg['RESULT_LIST']['CCD_LIST'] = list(ccd_list)
            self.f1_publisher.publish_message(body['REPLY_QUEUE'], msg)

        else:
            pytest.fail("The following unknown message was received by FWDR F1: %s" % body)


    def on_f2_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        if self.DP:
            print("In test_pp_dev - incoming on_f2_message")
            self.prp.pprint(body)
            print("\n----------------------\n\n")
        self.f2_consumer_msg_list.append(body)

        if body['MSG_TYPE'] == 'PP_FWDR_HEALTH_CHECK':
            msg = {}
            msg['MSG_TYPE'] = 'PP_FWDR_HEALTH_CHECK_ACK'
            msg['COMPONENT'] = 'FORWARDER_2'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            self.f2_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'PP_FWDR_XFER_PARAMS':
            msg = {}
            msg['MSG_TYPE'] = 'PP_FWDR_XFER_PARAMS_ACK'
            msg['COMPONENT'] = 'FORWARDER_2'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            self.f2_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'PP_FWDR_READOUT':
            # Find message in message list for xfer_params
            xfer_msg = None
            for msg in self.f2_consumer_msg_list:
                if msg['MSG_TYPE'] == 'PP_FWDR_XFER_PARAMS':
                    xfer_msg = msg
                    break
            if xfer_msg == None:
                pytest.fail("The PP_FWDR_XFER_PARAMS message was not received before AR_FWDR_READOUT in F2")

            # use message to build response
            msg = {}
            msg['MSG_TYPE'] = 'PP_FWDR_READOUT_ACK'
            msg['COMPONENT'] = 'FORWARDER_2'
            msg['JOB_NUM'] = xfer_msg['JOB_NUM']
            msg['IMAGE_ID'] = xfer_msg['IMAGE_ID']
            msg['ACK_ID'] = body['ACK_ID']
            msg['ACK_BOOL'] = True
            msg['RESULT_LIST'] = {}
            msg['RESULT_LIST']['CCD_LIST'] = []
            msg['RESULT_LIST']['RECEIPT_LIST'] = []
            ccd_list = xfer_msg['XFER_PARAMS']['CCD_LIST']
            receipt_list = []
            for i in range(0, len(ccd_list)):
                receipt_list.append('F2_Rec_x447_' + str(i))
            msg['RESULT_LIST']['RECEIPT_LIST'] = receipt_list
            msg['RESULT_LIST']['CCD_LIST'] = list(ccd_list)
            self.f2_publisher.publish_message(body['REPLY_QUEUE'], msg)

        else:
            pytest.fail("The following unknown message was received by FWDR F2: %s" % body)
