###############################################
# See README_PYTESTS for testing instructions #
###############################################

import pika
import redis
import yaml
import sys
import os
from pprint import pprint, pformat
from time import sleep
#import _thread
import threading
import pytest
import random
import logging
sys.path.insert(1, '../iip')
sys.path.insert(1, '../')
#import DMCS
import toolsmod
from toolsmod import get_timestamp
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from MessageAuthority import MessageAuthority
from const import *
from AuxDevice import *

#LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %'
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename='logs/AT_TEST.log', level=logging.DEBUG, format=LOG_FORMAT)

@pytest.fixture(scope='session')
def Atdev(request):
    atdev = AuxDevice('tests/yaml/L1SystemCfg_Test_at.yaml')
    request.addfinalizer(atdev.shutdown)
    return atdev

class TestAtDev:

    dmcs_pub_broker_url = None
    dmcs_publisher = None
    dmcs_consumer = None
    dmcs_consumer_msg_list = []

    at_ctrl_pub_broker_url = None
    at_ctrl_publisher = None
    at_ctrl_consumer = None
    at_ctrl_consumer_msg_list = []

    F99_pub_broker_url = None
    F99_publisher = None
    F99_consumer = None
    f99_consumer_msg_list = []

    EXPECTED_AR_CTRL_MESSAGES = 1
    EXPECTED_DMCS_MESSAGES = 1
    EXPECTED_F99_MESSAGES = 1

    ccd_list = [14,17,21.86]
    prp = toolsmod.prp
    DP = toolsmod.DP  # Debug Printing either True or False...override for this file only...


    def test_atdev(self, Atdev):
        self.atdev = Atdev
        try:
            cdm = toolsmod.intake_yaml_file('tests/yaml/L1SystemCfg_Test_at.yaml')
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
   
        """ 
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
        """
    
        F99_name = 'F99'
        F99_passwd = 'F99'
        F99_pub_name = 'F99_PUB'
        F99_pub_passwd = 'F99_PUB'
        F99_broker_url = "amqp://" + F99_name + ":" + \
                                F99_passwd + "@" + \
                                broker_addr
        F99_pub_broker_url = "amqp://" + F99_pub_name + ":" + \
                                    F99_pub_passwd + "@" + \
                                    broker_addr
        print("Opening publisher with this URL string: %s" % F99_pub_broker_url)
        self.F99_publisher = SimplePublisher(F99_pub_broker_url, "YAML")
   
        print("All publishers are running...")
 
        # Must be done before consumer threads are started
        # This is used for verifying message structure
        self._msg_auth = MessageAuthority()
        print("MessageAuthority running...")

        self.dmcs_consumer = Consumer(dmcs_broker_url,'dmcs_ack_consume', 'thread-dmcs',
                                     self.on_dmcs_message,'YAML')
        self.dmcs_consumer.start()

        print("DMCS Consumer running...")

        """
        self.ar_ctrl_consumer = Consumer(ar_ctrl_broker_url,'archive_ctrl_consume', 'thread-ar-ctrl', 
                                    self.on_ar_ctrl_message,'YAML')
        self.ar_ctrl_consumer.start()

        print("ar_ctrl Consumer running...")
        """

        self.F99_consumer = Consumer(F99_broker_url,'f99_consume', 'thread-f99', 
                                    self.on_f99_message,'YAML')
        self.F99_consumer.start()

        print("F99 Consumer running...")


        sleep(3)
        print("Test Setup Complete. Commencing Messages...")

        self.send_messages()
        sleep(8)
        self.verify_dmcs_messages()
        self.verify_F99_messages()
        #self.verify_ar_ctrl_messages()

        sleep(3)

        # Shut down consumer threads nicely
        self.dmcs_consumer.stop()
        self.dmcs_consumer.join()
        #self.ar_ctrl_consumer.stop()
        #self.ar_ctrl_consumer.join()
        self.F99_consumer.stop()
        self.F99_consumer.join()
        if self.DP:
            print("Finished with AT tests.")


    def send_messages(self):

        LOGGER.warning('In on_f99_message handler')
        print("Starting send_messages")
        # Tests only an AT device
        
        self.EXPECTED_AR_CTRL_MESSAGES = 2
        self.EXPECTED_DMCS_MESSAGES = 2
        self.EXPECTED_F99_MESSAGES = 4

        """
        msg = {}
        msg['MSG_TYPE'] = "AT_NEW_SESSION"
        msg['SESSION_ID'] = 'SI_469976'
        msg['ACK_ID'] = 'AT_NEW_SESSION_ACK_44221'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        #time.sleep(2)
        time.sleep(12)
        print("New Session Message")
        self.dmcs_publisher.publish_message("at_foreman_consume", msg)

        """
        LOGGER.warning('About to send start_int')
        msg = {}
        msg['MSG_TYPE'] = "AT_START_INTEGRATION"
        msg['JOB_NUM'] = '4xx72'
        msg['IMAGE_ID'] = 'IMG_444245'
        msg['IMAGE_INDEX'] = 2
        msg['IMAGE_SEQUENCE_NAME'] = 'XX_seq'
        msg['IMAGES_IN_SEQUENCE'] = 8
        msg['SESSION_ID'] = 'SI_469976'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'NEW_VISIT_ACK_76'
        msg['RAFT_LIST'] = ['WFS_RAFT']
        msg['RAFT_CCD_LIST'] = [['WFS_CCD']]
        time.sleep(12)
        LOGGER.warning('Here comes start_int message')
        print("Start Integration Message")
        self.dmcs_publisher.publish_message("at_foreman_consume", msg)
        LOGGER.warning('Just after publishing start_int message')

        #time.sleep(3)
        time.sleep(8)
        msg = {}
        msg['MSG_TYPE'] = "AT_END_READOUT"
        msg['JOB_NUM'] = '4xx72'
        msg['SESSION_ID'] = 'SI_469976'
        msg['IMAGE_ID'] = 'IMG_444245'
        msg['IMAGE_INDEX'] = 2
        msg['IMAGE_SEQUENCE_NAME'] = 'XX_seq'
        msg['IMAGES_IN_SEQUENCE'] = 8
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        msg['ACK_ID'] = 'AT_ACK_94671'
        #time.sleep(11)
        #time.sleep(3)
        print("AT END READOUT Message")
        self.dmcs_publisher.publish_message("at_foreman_consume", msg)

        time.sleep(5)

        msg = {}
        msg['MSG_TYPE'] = "AT_HEADER_READY"
        msg['IMAGE_ID'] = 'IMG_444245'
        msg['FILENAME'] = '/mnt/headers'
        msg['ACK_ID'] = 'AT_ACK_1444'
        msg['REPLY_QUEUE'] = 'dmcs_ack_consume'
        print("AT HEADER_READY Message")
        self.dmcs_publisher.publish_message("at_foreman_consume", msg)
        time.sleep(2)

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
   

    def verify_F99_messages(self):
        len_list = len(self.f99_consumer_msg_list)
        print("Number of messages is: %s" % len_list)
        if len_list != self.EXPECTED_F99_MESSAGES:
            print("Incorrect number of F99 messages received")
            pytest.fail('F99 simulator received incorrect number of messages.\nExpected %s but received %s'\
                        % (self.EXPECTED_F99_MESSAGES, len_list))

        # Now check num keys in each message first, then check for key errors
        for i in range(0, len_list):
            msg = self.f99_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False:
                print("This F99 message failed verification: ")
                self.prp.pprint(msg)
                pytest.fail("The following message to F99 failed when compared with the sovereign example: %s" % msg)

        print("Messages to F99 pass verification.")
  
   
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

    def on_f99_message(self, ch, method, properties, body):
        LOGGER.debug("Inside on_f99_message......")
        print("Inside on_f99_message test handler........")
        ch.basic_ack(method.delivery_tag)
        self.f99_consumer_msg_list.append(body)
        if body['MSG_TYPE'] == 'AT_FWDR_HEALTH_CHECK':
            LOGGER.debug('Message received by health check test code.  body is: %s', pformat(str(body)))
            msg = {}
            msg['MSG_TYPE'] = 'AT_FWDR_HEALTH_CHECK_ACK'
            msg['COMPONENT'] = 'FORWARDER_99'
            msg['ACK_BOOL'] = True 
            msg['ACK_ID'] = body['ACK_ID']
            if self.DP:
                print("In test - on_f99_message health check - sending ack: %s" % msg)
            self.F99_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'AT_FWDR_XFER_PARAMS':
            msg = {}
            msg['MSG_TYPE'] = 'AT_FWDR_XFER_PARAMS_ACK'
            msg['COMPONENT'] = 'FORWARDER_99'
            msg['ACK_BOOL'] = True 
            msg['ACK_ID'] = body['ACK_ID']
            self.F99_publisher.publish_message(body['REPLY_QUEUE'], msg)

        elif body['MSG_TYPE'] == 'AT_FWDR_HEADER_READY':
            # No need to ACK
            pass

        elif body['MSG_TYPE'] == 'AT_FWDR_END_READOUT':
            LOGGER.warning("Inside on_f99_message AT_FWDR_END_READOUT case...")

            xfer_msg = None
            image_id = body['IMAGE_ID']
            for msg in self.f99_consumer_msg_list:
                if msg['MSG_TYPE'] == 'AT_FWDR_XFER_PARAMS':
                    xfer_msg = msg
            if xfer_msg == None:
                LOGGER.warning("The AT_FWDR_XFER_PARAMS message was not received before AT_FWDR_READOUT in F99")
                fail_msg = "The AT_FWDR_XFER_PARAMS message was not received before AT_FWDR_READOUT in F99"
                pytest.fail("\n".join(fail_msg), pytrace=True)
            # use message to build response
            msg = {}
            msg['MSG_TYPE'] = 'AT_FWDR_END_READOUT_ACK'
            msg['COMPONENT'] = 'FORWARDER_99'
            msg['JOB_NUM'] = body['JOB_NUM']
            msg['SESSION_ID'] = body['SESSION_ID']
            msg['ACK_ID'] = body['ACK_ID']
            msg['ACK_BOOL'] = True
            
            msg['RESULT_SET'] = {}
            msg['RESULT_SET']['FILENAME_LIST'] = []
            msg['RESULT_SET']['CHECKSUM_LIST'] = []
            RAFT_PLUS_CCD_LIST = []
            FILENAME_LIST = []
            CHECKSUM_LIST = []
            target_location = xfer_msg['TARGET_LOCATION']
            FILENAME_LIST.append(target_location + "/" + image_id + ".fits")
            CHECKSUM_LIST.append('XXXXFFFF4444$$$$')
            msg['RESULT_SET']['FILENAME_LIST'] = FILENAME_LIST
            msg['RESULT_SET']['CHECKSUM_LIST'] = CHECKSUM_LIST
            self.F99_publisher.publish_message(body['REPLY_QUEUE'], msg)

        else:
            pytest.fail("The following unknown message was received by FWDR F99: %s" % body)


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





