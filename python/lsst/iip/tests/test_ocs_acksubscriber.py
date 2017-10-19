import subprocess 
import os
import sys
import traceback
import signal
import pytest
sys.path.insert(1, "../iip")
sys.path.insert(1, "../")
from Consumer import Consumer 
from MessageAuthority import MessageAuthority
from const import * 
import toolsmod 
from time import sleep
from copy import deepcopy 
from SimplePublisher import SimplePublisher


class TestOCS_AckSubscriber: 

    os.chdir("ocs/src")
    ackSubscriber = subprocess.Popen("./Test_AckSubscriber&", shell=True, preexec_fn=os.setsid)
    print("Preparing ackSubscriber ...")
    sleep(120) 

    cmdListener = subprocess.Popen("./Test_CommandListener&", shell=True, preexec_fn=os.setsid)
    print("Preparing cmdListener ...")
    sleep(10) 


    EXPECTED_OCS_MESSAGES = 12
    ocs_consumer_msg_list = [] 

    def test_ocs_acksubscriber(self): 
        try: 
            cdm = toolsmod.intake_yaml_file("/home/centos/src/git/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test_ocs_bridge.yaml")
        except IOError as e: 
            trace = traceback.print_exc() 
            emsg = "Unable to fine CFG Yaml file %s\n" % self._config_file 
            print(emsg + trace)
            sys.exit(101) 

        broker_addr = cdm[ROOT]["BASE_BROKER_ADDR"] 

        # dmcs publisher 
        dmcs_pub_name = cdm[ROOT]["DMCS_BROKER_PUB_NAME"]
        dmcs_pub_pwd = cdm[ROOT]["DMCS_BROKER_PUB_PASSWD"] 
        dmcs_broker_pub_url = "amqp://" + dmcs_pub_name + ":" + \
                                      dmcs_pub_pwd + "@" + \
                                      broker_addr 
        self.dmcs_publisher = SimplePublisher(dmcs_broker_pub_url, "YAML")

        # dmcs consumer
        dmcs_name = cdm[ROOT]["DMCS_BROKER_NAME"] 
        dmcs_pwd = cdm[ROOT]["DMCS_BROKER_PASSWD"]

        dmcs_broker_url = "amqp://" + dmcs_name + ":" + \
                                      dmcs_pwd + "@" + \
                                      broker_addr 

        self.dmcs_consumer = Consumer(dmcs_broker_url, "ocs_dmcs_consume", "thread-dmcs-consume", 
                                      self.on_ocs_message, "YAML", None) 
        self.dmcs_consumer.start()

        # ocs consumer from DMCS
        ocs_name = cdm[ROOT]["OCS_BROKER_NAME"] 
        ocs_pwd = cdm[ROOT]["OCS_BROKER_PASSWD"]

        # FIXME: New OCS account for consumer test_dmcs_ocs_publish 
        ocs_broker_url = "amqp://" + "AFM" + ":" +\
                                     "AFM" + "@" +\
                                     broker_addr 
        self.ocs_consumer = Consumer(ocs_broker_url, "test_dmcs_ocs_publish", "thread-ocs-consume",
                                     self.on_dmcs_message, "YAML", None) 
        self.ocs_consumer.start() 
        print("Test setup Complete. Commencing Messages...")

        self._msg_auth = MessageAuthority("/home/centos/src/git/ctrl_iip/python/lsst/iip/messages.yaml")

        self.send_messages() 
        sleep(10)

        os.killpg(os.getpgid(self.cmdListener.pid), signal.SIGTERM) 
        os.killpg(os.getpgid(self.ackSubscriber.pid), signal.SIGTERM) 

        print("MY OCS MESSAGES: %s" % self.ocs_consumer_msg_list) 
        self.verify_ocs_messages() 
        print("Finished with CommandListener tests.") 

    def send_messages(self): 
        os.chdir("../commands/")
        
        commands = ["start", "stop", "enable", "disable", "enterControl", "exitControl", "standby", "abort"] 
        #devices = ["archiver" , "catchuparchiver", "processingcluster"] 

        #for device in devices: 
        #    for command in commands: 
        #        cmd = None
        #        if command == "start": 
        #            cmd = "./sacpp_" + device + "_" + command + "_commander Normal"
        #        else: 
        #            cmd = "./sacpp_" + device + "_" + command + "_commander 0"
        #        p = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
        #        print("=== " + device.upper() + " " + command.upper() + " Message")
        #        sleep(10)  # this is not random. startup .sacpp_ thing takes about 7 seconds. 
        #        os.killpg(os.getpgid(p.pid), signal.SIGTERM) 

        device_sh = ["AR", "CU", "PP"]

        for device in device_sh: 
            my_dev = None 
            if device == "AR": 
                my_dev = "archiver"
            elif device == "CU": 
                my_dev = "catchuparchiver" 
            elif device == "PP": 
                my_dev = "processingcluster"
            cmd = "./sacpp_" + my_dev + "_SummaryState_log" 
            run = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
            sleep(10) 
            msg = {} 
            msg["MSG_TYPE"] = "SUMMARY_STATE_EVENT"
            msg["DEVICE"] = device
            msg["CURRENT_STATE"] = 0
            self.dmcs_publisher.publish_message("dmcs_ocs_publish", msg)  
            print("=== " + device.upper() + " SummaryState Controller Message")
            sleep(10)
            os.killpg(os.getpgid(run.pid), signal.SIGTERM) 

            cmd1 = "./sacpp_" + my_dev + "_SettingVersions_log" 
            run1 = subprocess.Popen(cmd1, shell=True, preexec_fn=os.setsid)
            sleep(10) 
            msg1 = {} 
            msg1["MSG_TYPE"] = "RECOMMENDED_SETTINGS_VERSION_EVENT"
            msg1["DEVICE"] = device
            msg1["CFG_KEY"] = "Normal"
            self.dmcs_publisher.publish_message("dmcs_ocs_publish", msg1)  
            print("=== " + device.upper() + " RecommendSettingsVersion Controller Message")
            sleep(10)
            os.killpg(os.getpgid(run1.pid), signal.SIGTERM) 

            cmd2 = "./sacpp_" + my_dev + "_AppliedSettingsMatchStart_log" 
            run2 = subprocess.Popen(cmd2, shell=True, preexec_fn=os.setsid)
            sleep(10) 
            msg2 = {} 
            msg2["MSG_TYPE"] = "APPLIED_SETTINGS_MATCH_START_EVENT"
            msg2["DEVICE"] = device
            msg2["SETTING"] = "Normal"
            msg2["APPLIED"] = True
            self.dmcs_publisher.publish_message("dmcs_ocs_publish", msg2)  
            print("=== " + device.upper() + " AppliedSettingsMatchStart Controller Message")
            sleep(10)
            os.killpg(os.getpgid(run2.pid), signal.SIGTERM) 

            cmd3 = "./sacpp_" + my_dev + "_ErrorCode_log" 
            run3 = subprocess.Popen(cmd3, shell=True, preexec_fn=os.setsid)
            sleep(10) 
            msg3 = {} 
            msg3["MSG_TYPE"] = "ERROR_CODE_EVENT"
            msg3["DEVICE"] = device
            msg3["ERROR_CODE"] = 0
            self.dmcs_publisher.publish_message("dmcs_ocs_publish", msg3)  
            print("=== " + device.upper() + " ErrorCode Controller Message")
            sleep(10)
            os.killpg(os.getpgid(run3.pid), signal.SIGTERM) 

            sleep(20)

        print("Message Sender Done.") 

    def verify_ocs_messages(self): 
        len_list = len(self.ocs_consumer_msg_list)
        if len_list != self.EXPECTED_OCS_MESSAGES: 
            pytest.fail("OCS simulator received incorrect number of messages.\n Expected %s but received %s" \
                    % (self.EXPECTED_OCS_MESSAGES, len_list))

        for i in range(0, len_list): 
            msg = self.ocs_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False: 
                pytest.fail("The following AckSubscriber response message failed when compared with the sovereign\
                             example: %s" % msg)
        print("Responses to OCS pass verification")

    def on_ocs_message(self, ch, method, properties, body): 
        ch.basic_ack(method.delivery_tag)
        msg = deepcopy(body)
        msg_type = msg["MSG_TYPE"]
        if msg_type == "START": 
            msg.pop("CFG_KEY", None) # pop CFG_KEY
        
        msg["MSG_TYPE"] = msg_type + "_ACK"
        msg["ACK_BOOL"] = True 
        msg["ACK_STATEMENT"] = "test" 
        print("MY BODY SENT: %s" % msg)
        
        self.dmcs_publisher.publish_message("dmcs_ocs_publish", msg)  

    def on_dmcs_message(self, ch, method, properties, body): 
        # ch.basic_ack(method.delivery_tag)
        self.ocs_consumer_msg_list.append(body)

    

