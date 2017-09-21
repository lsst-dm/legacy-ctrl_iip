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


class TestOCS_CommandListener: 

    dmcs_consumer = None
    dmcs_consumer_msg_list = [] 

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

        self.dmcs_consumer = Consumer(dmcs_broker_url, "YAML") 

        self._msg_auth = MessageAuthority()
        self.setup_consumers() 
        sleep(3) 
        print("Test Setup Complete. Commencing Messages...") 

        self.send_messages() 
        time.sleep(2)
        print("Finished with CommandListener tests.") 

    def setup_consumers(self): 
        try: 
            _thread.start_new_thread(self.run_dmcs_consumer, ("thread-test-dmcs_consume", 2,)) 
        except: 
            print("Bad trouble creating dmcs_consumer thread for testing...exiting...") 
            sys.exit(101) 

    def run_dmcs_consumer(self, threadname, delay): 
        self.dmcs_consumer.run(self.on_dmcs_message) 

    def run_ocs_commandlistener(self): 
        os.chdir("../ocs/src") 
        subprocess.call("./CommandListener", shell=True)
        time.sleep(3)

    def send_messages(self): 
        os.chdir("../ocs/commands")
        
        commands = ["start", "stop", "enable", "disable", "enterControl", "exitControl", "standby", "abort"] 
        devices = ["archiver", "catchuparchiver", "processingcluster"] 

        for device in devices: 
            for command in commands: 
                cmd = "./sacpp_" + device + "_" + command + "_commander 0"
                p = subprocess.Popen(cmd, shell=True, preexec_fn=os.setid)
                print("=== " + command.upper() + " Message")
                time.sleep(2) 
                os.killpg(os.getpgid(p.pid), signal.SIGTERM) 

        print("Message Sender Done.") 

    def verify_ocs_messages(self): 
        print("Messages received by verify_ocs_messages:")
        self.prp.pprint(self.dmcs_consumer_msg_list)
        len_list = len(self.dmcs_consumer_msg_list)
        if len_list != self.EXPECTED_DMCS_MESSAGES: 
            print("Messages received by verify_ocs_messages:")
            self.prp.pprint(self.dmcs_consumer_msg_list)
            pytest.fail("DMCS simulator received incorrect number of messages.\n Expected %s but received %s" \
                    % (self.EXPECTED_DMCS_MESSAGES, len_list))

        for i in range(0, len_list): 
            msg = self.dmcs_consumer_msg_list[i]
            result = self._msg_auth.check_message_shape(msg)
            if result == False: 
                pytest.fail("The following OCS Bridge response message failed when compared with the sovereign\
                             example: %s" % msg)
        print("Responses to DMCS pass verification")

    def clear_message_lists(self): 
        self.dmcs_consumer_msg_list = [] 


    def on_dmcs_message(self, ch, method, properties, body): 
        self.dmcs_consumer_msg_list.append(body)

def main(): 
    test = TestOCS_CommandListener() 
    test.run_ocs_commandlistener() 


if __name__ == "__main__": main() 

send_messages()
