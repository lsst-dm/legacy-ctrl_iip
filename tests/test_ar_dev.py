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
import toolsmod
from toolsmod import get_timestamp
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from MessageAuthority import MessageAuthority
from const import *
from ArchiveDevice import *

logging.basicConfig(filename='logs/ARCHIVE_TEST.log', level=logging.INFO, format=LOG_FORMAT)

@pytest.fixture(scope='session')
def Ardev(request):
    ardev = ArchiveDevice('tests/yaml/L1SystemCfg_Test_ar.yaml')
    request.addfinalizer(ardev.shutdown)
    return ardev

class TestArDev:

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
    NUM_READOUTS = 0

    ccd_list = [14,17,21.86]
    prp = toolsmod.prp
    DP = toolsmod.DP  # Debug Printing either True or False...override for this file only...


    def test_ardev(self, Ardev):
        self.ardev = Ardev
        try:
            cdm = toolsmod.intake_yaml_file('tests/yaml/L1SystemCfg_Test_ar.yaml')
        except IOError as e:
            trace = traceback.print_exc()
            emsg = "Unable to find CFG Yaml file %s\n" % self._config_file
            print(emsg + trace)
            raise  

        raft_dict = cdm[ROOT]['DEFAULT_RAFT_CONFIGURATION']
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
   
        print("All publishers are running...")
 
        # Must be done before consumer threads are started
        # This is used for verifying message structure
        self._msg_auth = MessageAuthority()
        print("MessageAuthority running...")

        self.dmcs_consumer = Consumer(dmcs_broker_url,'dmcs_ack_consume', 'thread-dmcs',
                                     self.on_dmcs_message,'YAML')
        self.dmcs_consumer.start()

        print("DMCS Consumer running...")

        self.ar_ctrl_consumer = Consumer(ar_ctrl_broker_url,'archive_ctrl_consume', 'thread-ar-ctrl', 
                                    self.on_ar_ctrl_message,'YAML')
        self.ar_ctrl_consumer.start()

        print("ar_ctrl Consumer running...")

        self.F1_consumer = Consumer(F1_broker_url,'f1_consume', 'thread-f1', 
                                    self.on_f1_message,'YAML')
        self.F1_consumer.start()

        print("F1 Consumer running...")

        self.F2_consumer = Consumer(F2_broker_url,'f2_consume', 'thread-f2', 
                                    self.on_f2_message,'YAML')
        self.F2_consumer.start()

        print("F2 Consumer running...")

        sleep(3)
        print("Test Setup Complete. Commencing Messages...")

        self.send_messages()
        sleep(8)
        self.verify_dmcs_messages()
        self.verify_ar_ctrl_messages()
        self.verify_F1_messages()
        self.verify_F2_messages()

        sleep(3)

        # Shut down consumer threads nicely
        self.dmcs_consumer.stop()
        self.dmcs_consumer.join()
        self.ar_ctrl_consumer.stop()
        self.ar_ctrl_consumer.join()
        self.F1_consumer.stop()
        self.F1_consumer.join()
        self.F2_consumer.stop()
        self.F2_consumer.join()
        if self.DP:
            print("Finished with AR tests.")


    def send_messages(self):

        print("Starting send_messages")
        # Tests only an AR device
        
        self.EXPECTED_AR_CTRL_MESSAGES = 2
        self.EXPECTED_DMCS_MESSAGES = 2
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
        msg['JOB_NUM'] = '4xx72'
        msg['SESSION_ID'] = 'SI_469976'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'NEW_VISIT_ACK_76'
        msg['RA'] = "231.221"
        msg['DEC'] = "-45.34"
        msg['ANGLE'] = "120.0"
        msg['RAFT_LIST'] = ['10','32','41','42','43']
        msg['RAFT_CCD_LIST'] = [['ALL'],['02','11','12'],['00','02'],['02','12','11','22','00'],['ALL']]
        time.sleep(2)
        print("Next Visit Message")
        self.dmcs_publisher.publish_message("ar_foreman_consume", msg)
          
        msg = {}
        msg['MSG_TYPE'] = "AR_TAKE_IMAGES"
        msg['JOB_NUM'] = '4xx72'
        msg['NUM_IMAGES'] = '4'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'ACK_44221'
        time.sleep(2)
        print("AR Take Images Message")
        self.dmcs_publisher.publish_message("ar_foreman_consume", msg)

        msg = {}
        msg['MSG_TYPE'] = "AR_END_READOUT"
        msg['JOB_NUM'] = '4xx72'
        msg['IMAGE_ID'] = 'IMG_444245'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'AR_ACK_94671'
        time.sleep(2)
        print("AR END READOUT Message")
        self.dmcs_publisher.publish_message("ar_foreman_consume", msg)
      
        msg = {}
        msg['MSG_TYPE'] = "AR_END_READOUT"
        msg['JOB_NUM'] = '4xx72'
        msg['IMAGE_ID'] = 'IMG_444246'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'AR_ACK_94673'
        time.sleep(2)
        print("AR END READOUT Message")
        self.dmcs_publisher.publish_message("ar_foreman_consume", msg)

        msg = {}
        msg['MSG_TYPE'] = "AR_END_READOUT"
        msg['JOB_NUM'] = '4xx72'
        msg['IMAGE_ID'] = 'IMG_444247'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'AR_ACK_94676'
        time.sleep(2)
        print("AR END READOUT Message")
        self.dmcs_publisher.publish_message("ar_foreman_consume", msg)

        msg = {}
        msg['MSG_TYPE'] = "AR_END_READOUT"
        msg['JOB_NUM'] = '4xx72'
        msg['IMAGE_ID'] = 'IMG_444248'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'AR_ACK_94677'
        time.sleep(2)
        print("AR END READOUT Message")
        self.dmcs_publisher.publish_message("ar_foreman_consume", msg)

        msg = {}
        msg['MSG_TYPE'] = "AR_TAKE_IMAGES_DONE"
        msg['JOB_NUM'] = '4xx72'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'ACK_44221'
        time.sleep(2)
        print("AR Take Images Done Message")
        self.dmcs_publisher.publish_message("ar_foreman_consume", msg)

        time.sleep(9)
        print("Message Sender done")


    def verify_dmcs_messages(self):
        len_list = len(self.dmcs_consumer_msg_list)
        print("DMCS RECEIVED %s MESSAGES" % len_list)
        if len_list != self.EXPECTED_DMCS_MESSAGES:
            print("Incorrect number of DMCS messages received")
            pytest.fail('DMCS simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_DMCS_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.dmcs_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                print("This DMCS message failed verification: ")
                self.prp.pprint(msg)
                pytest.fail("The following DMCS Bridge response message failed when compared with the sovereign example: %s" % msg)
        print("Responses to DMCS Bridge pass verification.")
   

    def verify_ar_ctrl_messages(self):
        len_list = len(self.ar_ctrl_consumer_msg_list)
        print("AR_CTRL RECEIVED %s MESSAGES" % len_list)
        if len_list != self.EXPECTED_AR_CTRL_MESSAGES:
            print("Incorrect number of AR_CTRL messages received")
            pytest.fail('AR CTRL simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_AR_CTRL_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.ar_ctrl_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                print("This AR_CTRL message failed verification: ")
                self.prp.pprint(msg)
                pytest.fail("The following message to the AR CTRL failed when compared with the sovereign example: %s" % msg)
        print("Messages to the AR CTRL pass verification.")
   

    def verify_F1_messages(self):
        len_list = len(self.f1_consumer_msg_list)
        print("F1 RECEIVED %s MESSAGES" % len_list)
        if len_list != self.EXPECTED_F1_MESSAGES:
            print("Incorrect number of F1 messages received")
            pytest.fail('F1 simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_F1_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.f1_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                print("This F1 message failed verification: ")
                self.prp.pprint(msg)
                pytest.fail("The following message to F1 failed when compared with the sovereign example: %s" % msg)

        print("Messages to F1 pass verification.")
  
   
    def verify_F2_messages(self):
        len_list = len(self.f2_consumer_msg_list)
        print("F2 RECEIVED %s MESSAGES" % len_list)
        if len_list != self.EXPECTED_F2_MESSAGES:
            print("Incorrect number of F2 messages received")
            pytest.fail('F2 simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_F2_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.f2_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                print("This F2 message failed verification: ")
                self.prp.pprint(msg)
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
            msg['TARGET_LOCATION'] = '/tmp' 
            self.ar_ctrl_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'AR_ITEMS_XFERD':
            msg = {}
            msg['MSG_TYPE'] = 'AR_ITEMS_XFERD_ACK'
            msg['COMPONENT'] = 'ARCHIVE_CTRL'
            msg['ACK_ID'] = body['ACK_ID']
            msg['ACK_BOOL'] = True
            filename_list = body['RESULT_SET']['FILENAME_LIST']
            msg['RESULT_SET'] = {}
            msg['RESULT_SET']['IMAGE_ID_LIST'] = body['RESULT_SET']['IMAGE_ID_LIST']
            msg['RESULT_SET']['RECEIPT_LIST'] = []
            msg['RESULT_SET']['FILENAME_LIST'] = filename_list
            RECEIPT_LIST = []
            for filename in filename_list:
                RECEIPT_LIST.append('x14_' + str(filename))
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

        elif body['MSG_TYPE'] == 'AR_FWDR_TAKE_IMAGES':
            # This message handler is not necessary as it does nothing
            # But it is explanatory in nature for understanding/maintaining the file.
            #
            # No ack necessary - but NUM_IMAGES param will be 
            # needed in AR_FWDR_TAKE_IMAGES_DONE message handler below
            pass

        elif body['MSG_TYPE'] == 'AR_FWDR_END_READOUT':
            self.NUM_READOUTS = self.NUM_READOUTS + 1

        elif body['MSG_TYPE'] == 'AR_FWDR_TAKE_IMAGES_DONE':
            # Find message in message list for xfer_params
            xfer_msg = None
            image_id_list = []
            num_images = 0
            for msg in self.f1_consumer_msg_list:
                if msg['MSG_TYPE'] == 'AR_FWDR_END_READOUT':
                    image_id_list.append(msg['IMAGE_ID'])
                if msg['MSG_TYPE'] == 'AR_FWDR_XFER_PARAMS':
                    xfer_msg = msg
                if msg['MSG_TYPE'] == 'AR_FWDR_TAKE_IMAGES':
                    num_images = int(msg['NUM_IMAGES'])
            if xfer_msg == None:
                pytest.fail("The AR_FWDR_XFER_PARAMS message was not received before AR_FWDR_READOUT in F1")

            # use message to build response
            msg = {}
            msg['MSG_TYPE'] = 'AR_FWDR_TAKE_IMAGES_DONE_ACK'
            msg['COMPONENT'] = 'FORWARDER_1'
            msg['JOB_NUM'] = xfer_msg['JOB_NUM']
            msg['ACK_ID'] = body['ACK_ID']
            raft_list = xfer_msg['XFER_PARAMS']['RAFT_LIST']
            raft_ccd_list = xfer_msg['XFER_PARAMS']['RAFT_CCD_LIST']
            msg['RESULT_SET'] = {}
            msg['RESULT_SET']['RAFT_LIST'] = raft_list
            msg['RESULT_SET']['RAFT_CCD_LIST'] = raft_ccd_list
            msg['RESULT_SET']['RAFT_PLUS_CCD_LIST'] = []
            msg['RESULT_SET']['FILENAME_LIST'] = []
            msg['RESULT_SET']['CHECKSUM_LIST'] = []
            RAFT_PLUS_CCD_LIST = []
            FILENAME_LIST = []
            CHECKSUM_LIST = []
            target_location = xfer_msg['TARGET_LOCATION']
            raft_plus_ccd_list = self.convert_raft_and_ccd_list_to_name_list(raft_list, raft_ccd_list)
            for ccd in raft_plus_ccd_list:
                RAFT_PLUS_CCD_LIST.append(ccd)
                ### XXX ADD IMAGE_ID from IMAGE_ID_LIST to target_dir and ccd name
                FILENAME_LIST.append(target_location + "/" + str(ccd))
                CHECKSUM_LIST.append('XXXXFFFF4444$$$$')
            msg['RESULT_SET']['RAFT_PLUS_CCD_LIST'] = RAFT_PLUS_CCD_LIST
            msg['RESULT_SET']['FILENAME_LIST'] = FILENAME_LIST
            msg['RESULT_SET']['CHECKSUM_LIST'] = CHECKSUM_LIST
            if num_images == self.NUM_READOUTS:
                msg['ACK_BOOL'] = True
            else:
                msg['ACK_BOOL'] = False
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

        elif body['MSG_TYPE'] == 'AR_FWDR_TAKE_IMAGES':
            # This message handler is not necessary as it does nothing
            # But it is explanatory in nature for understanding/maintaining the file.
            #
            # No ack necessary - but NUM_IMAGES param will be 
            # needed in AR_FWDR_TAKE_IMAGES_DONE message handler below
            pass


        elif body['MSG_TYPE'] == 'AR_FWDR_END_READOUT':
            pass

        elif body['MSG_TYPE'] == 'AR_FWDR_TAKE_IMAGES_DONE':
            # Find message in message list for xfer_params
            xfer_msg = None
            image_id_list = []
            num_images = 0;
            for msg in self.f2_consumer_msg_list:
                if msg['MSG_TYPE'] == 'AR_FWDR_END_READOUT':
                    image_id_list.append(msg['IMAGE_ID'])
                if msg['MSG_TYPE'] == 'AR_FWDR_XFER_PARAMS':
                    xfer_msg = msg
                if msg['MSG_TYPE'] == 'AR_FWDR_TAKE_IMAGES':
                    num_images = msg['NUM_IMAGES']
            if xfer_msg == None:
                pytest.fail("The AR_FWDR_XFER_PARAMS message was not received before AR_FWDR_READOUT in F1")

            # use message to build response
            msg = {}
            msg['MSG_TYPE'] = 'AR_FWDR_TAKE_IMAGES_DONE_ACK'
            msg['COMPONENT'] = 'FORWARDER_2'
            msg['JOB_NUM'] = xfer_msg['JOB_NUM']
            msg['ACK_ID'] = body['ACK_ID']
            msg['ACK_BOOL'] = True
            raft_list = xfer_msg['XFER_PARAMS']['RAFT_LIST']
            raft_ccd_list = xfer_msg['XFER_PARAMS']['RAFT_CCD_LIST']
            msg['RESULT_SET'] = {}
            msg['RESULT_SET']['RAFT_LIST'] = raft_list
            msg['RESULT_SET']['RAFT_CCD_LIST'] = raft_ccd_list
            msg['RESULT_SET']['RAFT_PLUS_CCD_LIST'] = []
            msg['RESULT_SET']['FILENAME_LIST'] = []
            msg['RESULT_SET']['CHECKSUM_LIST'] = []
            RAFT_PLUS_CCD_LIST = []
            FILENAME_LIST = []
            CHECKSUM_LIST = []
            target_location = xfer_msg['TARGET_LOCATION']
            raft_plus_ccd_list = self.convert_raft_and_ccd_list_to_name_list(raft_list, raft_ccd_list)
            for ccd in raft_plus_ccd_list:
                RAFT_PLUS_CCD_LIST.append(ccd)
                ### XXX ADD IMAGE_ID from IMAGE_ID_LIST to target_location and ccd name
                FILENAME_LIST.append(target_location + "/" + str(ccd))
                CHECKSUM_LIST.append('XXXXFFFF4444$$$$')
            msg['RESULT_SET']['RAFT_PLUS_CCD_LIST'] = RAFT_PLUS_CCD_LIST
            msg['RESULT_SET']['FILENAME_LIST'] = FILENAME_LIST
            msg['RESULT_SET']['CHECKSUM_LIST'] = CHECKSUM_LIST
            self.F2_publisher.publish_message(body['REPLY_QUEUE'], msg)

        else:
            pytest.fail("The following unknown message was received by FWDR F2: %s" % body)


    def convert_raftdict_to_name_list(self, rdict):
        raft_list = list(rdict.keys())
        num_rafts = len(raft_list)
        integrated_names_list = []
        for i in range(0,num_rafts):
            current_raft = raft_list[i]
            ccd_list = []
            ccd_list = rdict[current_raft]
            if ccd_list[0] == 'ALL':
                ccd_list = ['00','10','20','01','11','21','02','12','22']
            num_current_ccds = len(ccd_list)
            for j in range(0,num_current_ccds):
                tmp_str = current_raft + '-' + ccd_list[j]
                integrated_names_list.append(tmp_str)

        return integrated_names_list


    def convert_raft_and_ccd_list_to_name_list(self, raft_list, raft_ccd_list):
        #raft_list = list(rdict.keys())
        num_rafts = len(raft_list)
        integrated_names_list = []
        for i in range(0,num_rafts):
            current_raft = raft_list[i]
            ccd_list = []
            ccd_list = raft_ccd_list[i]
            if ccd_list[0] == 'ALL':
                ccd_list = ['00','10','20','01','11','21','02','12','22']
            num_current_ccds = len(ccd_list)
            for j in range(0,num_current_ccds):
                tmp_str = current_raft + '-' + ccd_list[j]
                integrated_names_list.append(tmp_str)

        return integrated_names_list





