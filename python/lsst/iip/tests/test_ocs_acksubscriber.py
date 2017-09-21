import subprocess 
import os
import sys
import time
import traceback
sys.path.insert(1, "../iip")
sys.path.insert(1, "../")
from Consumer import Consumer 
from MessageAuthority import MessageAuthority
from const import * 
import toolsmod 

class TestOCS_AckSubscriber: 
    def __init__(self): 
        try: 
            cdm = toolsmod.intake_yaml_file("/home/centos/ctrl_iip/python/lsst/iip/tests/yaml/L1SystemCfg_Test.yaml")
        except IOError as e: 
            trace = traceback.print_exc() 
            emsg = "Unable to fine CFG Yaml file %s\n" % self._config_file 
            print(emsg + trace)
            sys.exit(101) 

        broker_addr = cdm[ROOT]["BASE_BROKER_ADDR"] 

        dmcs_name = cdm[ROOT]["DMCS_BROKER_NAME"] 
        dmcs_pwd = cdm[ROOT]["DMCS_BROKER_PASSWD"]

        dmcs_broker_url = "amqp://" + dmcs_name + ":" + \
                                      dmcs_pwd + "@" + \
                                      broker_addr 

        self.dmcs_publisher = SimplePublisher(dmcs_broker_url, "YAML") 

        self._msg_auth = MessageAuthority()
        self.setup_consumers() 
        sleep(3) 
        print("Test Setup Complete. Commencing Messages...") 

        self.send_messages() 
        time.sleep(2)
        print("Finished with AckSubscriber tests.")

    def setup_consumers(self): 
        try: 
            _thread.start_new_thread(self.run_ocs_command_listener, ("thread-test-ocs_command_listener", 2,)) 
        except: 
            print("Bad trouble creating dmcs_consumer thread for testing...exiting...") 
            sys.exit(101) 

    def run_ocs_command_listener(self, threadname, delay): 
        os.chdir("../ocs/commands")
        subprocess.call("./sacpp_archiver_enable_controller")

    def run_ocs_acksubscriber(self): 
        os.chdir("../ocs/src") 
        subprocess.call("./AckSubscriber", shell=True)
        time.sleep(30) # fine tune about this one

    def send_messages(self): 

        commands = ["START", "STOP", "ENABLE", "DISABLE", "ENTERCONTROL", "EXITCONTROL", "STANDBY", "ABORT"] 
        devices = ["AR", "CU", "PP"] 
        
        for device in devices: 
            for command in commands: 
                msg = {} 
                msg["MSG_TYPE"] = commands + "_ACK"
                msg["DEVICE"] = device 
                msg["ACK_ID"] = "test_ack_" + str(ack_count)
                msg["ACK_BOOL"] = True
                msg["ACK_STATEMENT"] = "test works."
                msg["CMD_ID"] = "123456789" # this needs to be discussed
                self.dmcs_publisher.publish_message("dmcs_ocs_publish", msg) 
                print("=== " + msg["MSG_TYPE"]  + " Message is sent.")
                time.sleep(2) 

        for device in devices: 
            msg["MSG_TYPE"] = "SUMMARY_STATE_EVENT"
            msg["DEVICE"] = device 
            msg["CURRENT_STATE"] = 1 # this needs to be discussed
            self.dmcs_publisher.publish_message("dmcs_ocs_publish", msg)
            print("=== SUMMARY_STATE_EVENT is sent for %s" % device)
            time.sleep(2) 

        for device in devices: 
            msg["MSG_TYPE"] = "RECOMMENDED_SETTINGS_VERSION_EVENT"
            msg["DEVICE"] = device 
            msg["CFG_KEY"] = device.upper() + "-Normal" 
            self.dmcs_publisher.publish_message("dmcs_ocs_publish", msg)
            print("=== RECOMMENDED_SETTINGS_VERSION_EVENT is sent for %s" % device)
            time.sleep(2) 

        for device in devices: 
            msg["MSG_TYPE"] = "SETTINGS_APPLIED_EVENT"
            msg["DEVICE"] = device 
            msg["SETTING"] = device.upper() + "-Normal" 
            msg["APPLIED"] = True 
            self.dmcs_publisher.publish_message("dmcs_ocs_publish", msg)
            print("=== SETTINGS_APPLIED_EVENT is sent for %s" % device)
            time.sleep(2) 

        for device in devices: 
            msg["MSG_TYPE"] = "APPLIED_SETTINGS_MATCH_START_EVENT"
            msg["DEVICE"] = device 
            msg["APPLIED"] = True 
            self.dmcs_publisher.publish_message("dmcs_ocs_publish", msg)
            print("=== APPLIED_SETTINGS_MATCH_START_EVENT is sent for %s" % device)
            time.sleep(2) 

        for device in devices: 
            msg["MSG_TYPE"] = "ERROR_CODE_EVENT" 
            msg["DEVICE"] = device 
            msg["ERROR_CODE"] = 1 
            self.dmcs_publisher.publish_message("dmcs_ocs_publish", msg)
            print("=== ERROR_CODE_EVENT is sent for %s" % device)
            time.sleep(2) 

        print("Message Sender Done.") 

def main(): 
    test = TestOCS_AckSubscriber() 
    test.run_ocs_acksubscriber() 


if __name__ == "__main__": main() 

