import os 
from time import sleep 
import sys 
sys.path.insert(1, "../iip")
sys.path.insert(1, "../") 
from Consumer import Consumer 
from SimplePublisher import SimplePublisher 
from MessageAuthority import MessageAuthority 
from const import * 
import toolsmod
import pytest
from ArchiveController import ArchiveController 

class TestAR_Ctrl: 
    arctrl = ArchiveController("/home/centos/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test_ar-ctrl.yaml")

    ar_consumer_msg_list = [] 

    EXPECTED_AR_DEV_MESSAGES = 2
    VISIT_ID = "V_1213"
    IMAGE_ID = "IMG_13241"
    SEND_TO_AR = "archive_ctrl_consume"
    ACK_FROM_CTRL = "ar_foreman_ack_publish" 

    def test_ar_ctrl(self): 
        try:
            cdm = toolsmod.intake_yaml_file('/home/centos/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test_ar-ctrl.yaml')
        except IOError as e:
            trace = traceback.print_exc()
            emsg = "Unable to find CFG Yaml file %s\n" % self._config_file
            print(emsg + trace)
            sys.exit(101)
    
        broker_addr = cdm[ROOT]['BASE_BROKER_ADDR']
        afm_name = cdm[ROOT]["AFM_BROKER_NAME"]   
        afm_pwd = cdm[ROOT]["AFM_BROKER_PASSWD"] 

        afm_pub_name = cdm[ROOT]["AFM_BROKER_PUB_NAME"] 
        afm_pub_pwd = cdm[ROOT]["AFM_BROKER_PUB_PASSWD"] 

        self.xfer_root = cdm[ROOT]["ARCHIVE"]["ARCHIVE_XFER_ROOT"] 

        ar_dev_pub_broker_url = "amqp://" + afm_pub_name + ":" +\
                                afm_pub_pwd + "@" +\
                                broker_addr
        self.ar_dev_publisher = SimplePublisher(ar_dev_pub_broker_url, "YAML")

        ar_dev_broker_url = "amqp://" + afm_name + ":" +\
                            afm_pwd + "@" +\
                            broker_addr 
        self.ar_dev_consumer = Consumer(ar_dev_broker_url, self.ACK_FROM_CTRL, "thread-ar-dev", 
                                        self.on_ar_message, "YAML", None) 
        self.ar_dev_consumer.start()
        print("Test setup Complete. Commencing Messages...") 

        self._msg_auth = MessageAuthority('/home/centos/src/git/ctrl_iip/python/lsst/iip/messages.yaml')

        self.send_messages()
        sleep(10) 

        self.verify_ar_messages() 
        self.verify_path_files() 
        print("Finished with AR CTRL tests.") 

    def send_messages(self): 
        # msg = {} 
        # msg["MSG_TYPE"] = "ARCHIVE_HEALTH_CHECK" 
        # msg["SESSION_ID"] = "SI_314161"
        # msg["ACK_ID"] = "AR_ACK_10001"
        # self.ar_dev_publisher.publish_message(self.SEND_TO_AR, msg)  
        # print("ARCHIVE_HEALTH_CHECK Message")
        # sleep(2) 


        msg = {} 
        msg["MSG_TYPE"] = "NEW_ARCHIVE_ITEM" 
        msg["ACK_ID"] = "NEW_AR_10002"
        msg["JOB_NUM"] = "job_101"
        msg["SESSION_ID"] = "SI_314162" 
        msg["VISIT_ID"] = self.VISIT_ID
        msg["IMAGE_ID"] = self.IMAGE_ID 
        msg["REPLY_QUEUE"] = "ar_foreman_ack_publish" 
        self.ar_dev_publisher.publish_message(self.SEND_TO_AR, msg) 
        print("NEW_ARCHIVE_ITEM Message") 
        sleep(2) 


        msg = {} 
        msg["MSG_TYPE"] = "AR_ITEMS_XFERD" 
        msg["ACK_ID"] = "AR_ACK_10003" 
        msg["IMAGE_ID"] = "IMG_103" 
        msg["REPLY_QUEUE"] = "ar_foreman_ack_publish" 
        msg["RESULT_LIST"] = {} 
        msg["RESULT_LIST"]["CCD_LIST"] = ["101", "102"] 
        msg["RESULT_LIST"]["FILENAME_LIST"] = ["img1_ccd101", "img1_ccd102"] 
        msg["RESULT_LIST"]["CHECKSUM_LIST"] = ["F8DC17E983616D492A41344D736AD5D9", "99158C7DFD8351C9DEBC124029421993"] 
        self.ar_dev_publisher.publish_message(self.SEND_TO_AR, msg) 
        print("AR_ITEMS_XFERD Message") 
        sleep(2) 

    def clear_message_lists(self): 
        self.ar_consumer_msg_list = [] 

    def verify_ar_messages(self): 
        len_list = len(self.ar_consumer_msg_list)
        if len_list != self.EXPECTED_AR_DEV_MESSAGES: 
            pytest.fail("ArchiveController simulator received incorrect number of messages.\n" + 
                        "Expected %s but received %s" % (self.EXPECTED_AR_DEV_MESSAGES, len_list)) 

        for i in range(0, len_list): 
            msg = self.ar_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg) 
            if not result: 
                pytest.fail("The following message to Archive Device failed when\
                             compared with the sovereign example: %s" % msg) 

        print("Message to ArchiveDevice pass verification") 

    def verify_path_files(self): 
        path = self.xfer_root +  self.VISIT_ID + "/" + self.IMAGE_ID
        if not os.path.isdir(path): 
            pytest.fail("The following directory was not created by Archive Controller \
                         during the NEW_ARCHIVE_ITEM phase: %s" % path) 
        print("Path creation during NEW_ARCHIVE_ITEM phase pass verification") 

    def on_ar_message(self, ch, method, properties, body): 
        # ch.basic_ack(method.delivery_tag)
        self.ar_consumer_msg_list.append(body) 

