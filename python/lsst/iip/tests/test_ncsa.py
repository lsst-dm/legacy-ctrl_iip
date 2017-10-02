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
    D1_consumer_msg_list = []

    D2_pub_broker_url = None
    D2_publisher = None
    D2_consumer = None
    D2_consumer_msg_list = []

    EXPECTED_NCSA_MESSAGES = 1
    EXPECTED_DMCS_MESSAGES = 1
    EXPECTED_D1_MESSAGES = 1
    EXPECTED_D2_MESSAGES = 1

    ccd_list = [14,17,21,86]
    prp = toolsmod.prp


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

        self.EXPECTED_NCSA_MESSAGES = 3
        self.EXPECTED_DMCS_MESSAGES = 4
        self.EXPECTED_F1_MESSAGES = 3
        self.EXPECTED_F2_MESSAGES = 3

        msg = {}
        msg['MSG_TYPE'] = "NCSA_NEW_SESSION"
        msg['SESSION_ID'] = 'SI_469976'
        msg['ACK_ID'] = 'NCSA_NEW_SESSION_ACK_44221'
        msg['REPLY_QUEUE'] = 'pp_foreman_ack_publish'
        time.sleep(3)
        print("New Session Message")
        self.pp_publisher.publish_message("ncsa_consume", msg)

        msg = {}
        msg['MSG_TYPE'] = "NCSA_NEXT_VISIT"
        msg['VISIT_ID'] = 'XX_28272' 
        msg['SESSION_ID'] = 'NNV_469976'
        msg['REPLY_QUEUE'] = 'pp_foreman_ack_publish'
        msg['ACK_ID'] = 'NCSA_NEW_VISIT_ACK_76'
        msg['BORE_SIGHT'] = "231,123786456342, -45.3457156906, FK5"
        time.sleep(2)
        print("Next Visit Message")
        self.pp_publisher.publish_message("ncsa_consume", msg)

        """ 
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
        self.dmcs_publisher.publish_message("pp_foreman_consume", msg)
        """

        time.sleep(2)

        print("Message Sender done")


    def verify_dmcs_messages(self):
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
        print("Messages received by verify_ncsa_messages:")
        self.prp.pprint(self.ncsa_consumer_msg_list)
        len_list = len(self.ncsa_consumer_msg_list)
        if len_list != self.EXPECTED_NCSA_MESSAGES:
            print("Messages received by verify_ncsa_messages:")
            self.prp.pprint(self.ncsa_consumer_msg_list)
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
        print("Messages received by verify_F1_messages:")
        self.prp.pprint(self.f1_consumer_msg_list)
        len_list = len(self.f1_consumer_msg_list)
        if len_list != self.EXPECTED_F1_MESSAGES:
            print("Messages received by verify_F1_messages:")
            self.prp.pprint(self.f1_consumer_msg_list)
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
        print("Messages received by verify_F2_messages:")
        self.prp.pprint(self.f2_consumer_msg_list)
        len_list = len(self.f2_consumer_msg_list)
        if len_list != self.EXPECTED_F2_MESSAGES:
            print("Messages received by verify_F2_messages:")
            self.prp.pprint(self.f2_consumer_msg_list)
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
        self.dmcs_consumer_msg_list.append(body)

    def on_pp_message(self, ch, method, properties, body):
        # on_ncsa_publish
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
     

    def on_d1_message(self, ch, method, properties, body):
        self.d1_consumer_msg_list.append(body)
        if body['MSG_TYPE'] == 'DISTRIBUTOR_HEALTH_CHECK':
            msg = {}
            msg['MSG_TYPE'] = 'DISTRIBUTOR_HEALTH_CHECK_ACK'
            msg['COMPONENT'] = 'DISTRIBUTOR_1'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            self.f1_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'DISTRIBUTOR_XFER_PARAMS':
            msg = {}
            msg['MSG_TYPE'] = 'DISTRIBUTOR_XFER_PARAMS_ACK'
            msg['COMPONENT'] = 'DISTRIBUTOR_1'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            self.f1_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'DISTRIBUTOR_READOUT':
            # Find message in message list for xfer_params
            xfer_msg = None
            for msg in self.f1_consumer_msg_list:
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
            self.f1_publisher.publish_message(body['REPLY_QUEUE'], msg)

        else:
            pytest.fail("The following unknown message was received by D1: %s" % body)


    def on_d2_message(self, ch, method, properties, body):
        self.d2_consumer_msg_list.append(body)
        if body['MSG_TYPE'] == 'DISTRIBUTOR_HEALTH_CHECK':
            msg = {}
            msg['MSG_TYPE'] = 'DISTRIBUTOR_HEALTH_CHECK_ACK'
            msg['COMPONENT'] = 'DISTRIBUTOR_2'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            self.f2_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'DISTRIBUTOR_XFER_PARAMS':
            msg = {}
            msg['MSG_TYPE'] = 'DISTRIBUTOR_XFER_PARAMS_ACK'
            msg['COMPONENT'] = 'DISTRIBUTOR_2'
            msg['ACK_BOOL'] = True
            msg['ACK_ID'] = body['ACK_ID']
            self.f2_publisher.publish_message(body['REPLY_QUEUE'], msg)

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
            self.f2_publisher.publish_message(body['REPLY_QUEUE'], msg)

        else:
            pytest.fail("The following unknown message was received by D2: %s" % body)
