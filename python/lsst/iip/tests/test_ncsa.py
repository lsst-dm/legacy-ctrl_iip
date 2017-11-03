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
import NcsaForeman
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from MessageAuthority import MessageAuthority
from const import *
import toolsmod

from NcsaForeman import *

logging.basicConfig(filename='logs/NCSA_TEST.log', level=logging.INFO, format=LOG_FORMAT)

class TestNcsa:
    ncsa = NcsaForeman('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test_ncsa.yaml')

    pp_pub_broker_url = None
    pp_publisher = None
    pp_consumer = None
    pp_consumer_msg_list = []

    D1_pub_broker_url = None
    D1_publisher = None
    D1_consumer = None
    d1_consumer_msg_list = []

    D2_pub_broker_url = None
    D2_publisher = None
    D2_consumer = None
    d2_consumer_msg_list = []

    EXPECTED_PP_MESSAGES = 1
    EXPECTED_D1_MESSAGES = 1
    EXPECTED_D2_MESSAGES = 1

    ccd_list = [14,17,21,86]
    prp = toolsmod.prp
    DP = toolsmod.DP


    def test_ncsa(self):
        try:
            cdm = toolsmod.intake_yaml_file('/home/FM/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test.yaml')
        except IOError as e:
            trace = traceback.print_exc()
            emsg = "Unable to find CFG Yaml file %s\n" % self._config_file
            print(emsg + trace)
            sys.exit(101)
    
        broker_addr = cdm[ROOT]['BASE_BROKER_ADDR']
    
        pp_name = cdm[ROOT]['PFM_BROKER_NAME']
        pp_passwd = cdm[ROOT]['PFM_BROKER_PASSWD']
        pp_pub_name = cdm[ROOT]['PFM_BROKER_PUB_NAME']
        pp_pub_passwd = cdm[ROOT]['PFM_BROKER_PUB_PASSWD']
        pp_broker_url = "amqp://" + pp_name + ":" + \
                                pp_passwd + "@" + \
                                broker_addr
        pp_pub_broker_url = "amqp://" + pp_pub_name + ":" + \
                                    pp_pub_passwd + "@" + \
                                    broker_addr
        self.pp_publisher = SimplePublisher(pp_pub_broker_url, "YAML")
    
        D1_name = 'D1'
        D1_passwd = 'D1'
        D1_pub_name = 'D1_PUB'
        D1_pub_passwd = 'D1_PUB'
        D1_broker_url = "amqp://" + D1_name + ":" + \
                                D1_passwd + "@" + \
                                broker_addr
        D1_pub_broker_url = "amqp://" + D1_pub_name + ":" + \
                                    D1_pub_passwd + "@" + \
                                    broker_addr
        self.d1_publisher = SimplePublisher(D1_pub_broker_url, "YAML")
   
        D2_name = 'D2'
        D2_passwd = 'D2'
        D2_pub_name = 'D2_PUB'
        D2_pub_passwd = 'D2_PUB'
        D2_broker_url = "amqp://" + D2_name + ":" + \
                                D2_passwd + "@" + \
                                broker_addr
        D2_pub_broker_url = "amqp://" + D2_pub_name + ":" + \
                                    D2_pub_passwd + "@" + \
                                    broker_addr
        self.d2_publisher = SimplePublisher(D2_pub_broker_url, "YAML")
   
 
        # Must be done before consumer threads are started
        # This is used for verifying message structure
        self._msg_auth = MessageAuthority()

        self.pp_consumer = Consumer(pp_broker_url,'pp_foreman_ack_publish', 'thread-pp',
                                     self.on_pp_message,'YAML', None)
        self.pp_consumer.start()


        self.D1_consumer = Consumer(D1_broker_url,'d1_consume', 'thread-d1', 
                                    self.on_d1_message,'YAML', None)
        self.D1_consumer.start()


        self.D2_consumer = Consumer(D2_broker_url,'d2_consume', 'thread-d2', 
                                    self.on_d2_message,'YAML', None)
        self.D2_consumer.start()


        sleep(3)
        print("Test Setup Complete. Commencing Messages...")

        self.send_messages()
        sleep(14)
        self.verify_pp_messages()
        self.verify_D2_messages()
        self.verify_D1_messages()

        sleep(2)
        print("Finished with NCSA tests.")
        #sys.exit(0)


    def send_messages(self):

        print("Starting send_messages")
        # Tests only an AR device
        
        # self.clear_message_lists()

        self.EXPECTED_PP_MESSAGES = 4
        self.EXPECTED_D1_MESSAGES = 3
        self.EXPECTED_D2_MESSAGES = 3

        msg = {}
        msg['MSG_TYPE'] = "NCSA_NEW_SESSION"
        msg['SESSION_ID'] = 'SI_469976'
        msg['ACK_ID'] = 'NCSA_NEW_SESSION_ACK_44221'
        msg['REPLY_QUEUE'] = 'pp_foreman_ack_publish'
        time.sleep(1)
        print("New Session Message")
        self.pp_publisher.publish_message("ncsa_consume", msg)

        msg = {}
        msg['MSG_TYPE'] = "NCSA_NEXT_VISIT"
        msg['VISIT_ID'] = 'XX_28272' 
        msg['SESSION_ID'] = 'NNV_469976'
        msg['REPLY_QUEUE'] = 'pp_foreman_ack_publish'
        msg['ACK_ID'] = 'NCSA_NEW_VISIT_ACK_76'
        msg['BORE_SIGHT'] = "231,123786456342, -45.3457156906, FK5"
        time.sleep(1)
        print("Next Visit Message")
        self.pp_publisher.publish_message("ncsa_consume", msg)

        msg = {}
        msg['MSG_TYPE'] = "NCSA_START_INTEGRATION"
        msg['JOB_NUM'] = '4xx72'
        msg['IMAGE_ID'] = 'IMG_444244'
        msg['VISIT_ID'] = 'V14494'
        msg['SESSION_ID'] = '4_14_7211511'
        msg['REPLY_QUEUE'] = 'pp_foreman_ack_publish'
        msg['ACK_ID'] = 'PP_ACK_94671'
        msg['CCD_LIST'] = [4,14,16,17,29,35,36]
        time.sleep(2)
        msg['FORWARDERS'] = {}
        forwarder_list = ['FORWARDER_2', 'FORWARDER_1']
        ccd_list = [[17,18,111,126],[128,131,132]]
        msg['FORWARDERS']['FORWARDER_LIST'] = forwarder_list
        msg['FORWARDERS']['CCD_LIST'] = ccd_list
        self.pp_publisher.publish_message("ncsa_consume", msg)
        time.sleep(7)
        msg = {}
        msg['MSG_TYPE'] = "NCSA_READOUT"
        msg['JOB_NUM'] = '4xx72'
        msg['IMAGE_ID'] = 'IMG_444244'
        msg['VISIT_ID'] = 'V14494'
        msg['SESSION_ID'] = '4_14_7211511'
        msg['REPLY_QUEUE'] = 'pp_foreman_ack_publish'
        msg['ACK_ID'] = 'NCSA_READOUT_ACK_44221'
        time.sleep(2)
        self.pp_publisher.publish_message("ncsa_consume", msg)

        time.sleep(2)

        print("Message Sender done")


    def verify_pp_messages(self):
        len_list = len(self.pp_consumer_msg_list)
        if len_list != self.EXPECTED_PP_MESSAGES:
            pytest.fail('PP simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_PP_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.pp_consumer_msg_list[i]
            if msg['MSG_TYPE'] == 'NCSA_START_INTEGRATION_ACK':
                result = self.check_start_int_ack(msg)
            else:
                result = self._msg_auth.check_message_shape(msg)

            if result == False:
                pytest.fail("The following message to the PP Foreman failed when compared with the sovereign example: %s" % msg)
        print("Messages to the PP Foreman pass verification.")

    def check_start_int_ack(self, msg):
        """the PAIRS param in the message is a list. Every item in the list is a dictionary.
           because it is not known how many entried will be on the list, the dictionaries
           are deepcopied and checked against the MessageAuthority and check one at a time.
           In the meanwhile, the shape of the incoming message without the dictionaries and the
           PAIRS list set to None is checked against the MessageAuthority.

            BTW, because the individual dictionaries do not have a MSG_TYPE, one is 
            added to each dictionary to be checked so the dict to compare to can be 
            located in the messages.yaml file.
        """
        c_msg = deepcopy(msg)
        pairs = deepcopy(c_msg['PAIRS'])
        c_msg['PAIRS'] = None
        overall_shape = self._msg_auth.check_message_shape(c_msg)
        if overall_shape == False:
            return False

        for i in range (0, len(pairs)):
            pairs[i]['MSG_TYPE'] = 'PAIR'
            result = self._msg_auth.check_message_shape(pairs[i])
            if result == False:
                return False

        return True
   

    def verify_D1_messages(self):
        len_list = len(self.d1_consumer_msg_list)
        if len_list != self.EXPECTED_D1_MESSAGES:
            print("Messages received by verify_D1_messages:")
            self.prp.pprint(self.f1_consumer_msg_list)
            pytest.fail('F1 simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_D1_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.d1_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                pytest.fail("The following message to D1 failed when compared with the sovereign example: %s" % msg)
            else:
                print("Messages to D1 pass verification.")
  
   
    def verify_D2_messages(self):
        len_list = len(self.d2_consumer_msg_list)
        if len_list != self.EXPECTED_D2_MESSAGES:
            print("Messages received by verify_D2_messages:")
            self.prp.pprint(self.d2_consumer_msg_list)
            pytest.fail('D2 simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_D2_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.d2_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                pytest.fail("The following message to D2 failed when compared with the sovereign example: %s" % msg)
            else:
                print("Messages to D2 pass verification.")
  
 
    def on_pp_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        self.pp_consumer_msg_list.append(body)


    def on_d1_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        self.d1_consumer_msg_list.append(body)
        if body['MSG_TYPE'] == 'DISTRIBUTOR_HEALTH_CHECK':
            msg = {}
            msg['MSG_TYPE'] = 'DISTRIBUTOR_HEALTH_CHECK_ACK'
            msg['COMPONENT'] = 'DISTRIBUTOR_1'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            self.d1_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'DISTRIBUTOR_XFER_PARAMS':
            msg = {}
            msg['MSG_TYPE'] = 'DISTRIBUTOR_XFER_PARAMS_ACK'
            msg['COMPONENT'] = 'DISTRIBUTOR_1'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            self.d1_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'DISTRIBUTOR_READOUT':
            # Find message in message list for xfer_params
            xfer_msg = None
            for msg in self.d1_consumer_msg_list:
                if msg['MSG_TYPE'] == 'DISTRIBUTOR_XFER_PARAMS':
                    xfer_msg = msg
                    break
            if xfer_msg == None:
                pytest.fail("The DISTRIBUTOR_XFER_PARAMS message was not received before DISTRIBUTOE_READOUT in D1")

            # use message to build response
            msg = {}
            msg['MSG_TYPE'] = 'DISTRIBUTOR_READOUT_ACK'
            msg['COMPONENT'] = 'DISTRIBUTOR_1'
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
            self.d1_publisher.publish_message(body['REPLY_QUEUE'], msg)

        else:
            pytest.fail("The following unknown message was received by D1: %s" % body)


    def on_d2_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        self.d2_consumer_msg_list.append(body)
        if body['MSG_TYPE'] == 'DISTRIBUTOR_HEALTH_CHECK':
            msg = {}
            msg['MSG_TYPE'] = 'DISTRIBUTOR_HEALTH_CHECK_ACK'
            msg['COMPONENT'] = 'DISTRIBUTOR_2'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            self.d2_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'DISTRIBUTOR_XFER_PARAMS':
            msg = {}
            msg['MSG_TYPE'] = 'DISTRIBUTOR_XFER_PARAMS_ACK'
            msg['COMPONENT'] = 'DISTRIBUTOR_2'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            self.d2_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'DISTRIBUTOR_READOUT':
            # Find message in message list for xfer_params
            xfer_msg = None
            for msg in self.d2_consumer_msg_list:
                if msg['MSG_TYPE'] == 'DISTRIBUTOR_XFER_PARAMS':
                    xfer_msg = msg
                    break
            if xfer_msg == None:
                pytest.fail("The DISTRIBUTOR_XFER_PARAMS message was not received before DISTRIBUTOR_READOUT in D2")

            # use message to build response
            msg = {}
            msg['MSG_TYPE'] = 'DISTRIBUTOR_READOUT_ACK'
            msg['COMPONENT'] = 'DISTRIBUTOR_2'
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
            self.d2_publisher.publish_message(body['REPLY_QUEUE'], msg)

        else:
            pytest.fail("The following unknown message was received by D2: %s" % body)
