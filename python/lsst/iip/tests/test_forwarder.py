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


class Test_Forwarder: 

    os.chdir("forwarder/src")
    cmd = subprocess.Popen("./Forwarder&", shell=True, preexec_fn=os.setsid)
    sleep(10) 

    fwdr_consumer_msg_list = [] 

    def test_forwarder(self): 
        try: 
            cdm = toolsmod.intake_yaml_file("yaml/L1SystemCfg_Test_forwarder.yaml")
        except IOError as e: 
            trace = traceback.print_exc() 
            emsg = "Unable to find CFG Yaml file %s\n" % self._config_file 
            print(emsg + trace)
            sys.exit(101) 

        from_foreman_consume = cdm[ROOT]
        broker_addr = cdm[ROOT]['BASE_BROKER_ADDR'] 
        ar_pub_name = cdm[ROOT]['AFM_BROKER_PUB_NAME']
        ar_pub_pwd = cdm[ROOT]['AFM_BROKER_PUB_PASSWD']
        base_broker_url = 'amqp://' +\
                          ar_pub_name + ':' +\
                          ar_pub_pwd + '@' +\
                          broker_addr 
        print('Building base_broker_url. Result is %s' % base_broker_url) 
        
        ar_publisher = SimplePublisher(base_broker_url)  
        print("Test setup Complete. Commencing Messages...")

        sleep(10)

        os.killpg(os.getpgid(self.cmd.pid), signal.SIGTERM) 
        self.verify_ocs_messages() 
        print("Finished with Forwarder tests.") 

    def send_messages(self): 
        msg = {} 
        msg['MSG_TYPE'] = 'AR_FWDR_XFER_PARAMS' 
        msg['SESSION_ID'] = 'session_v771' 
        msg['VISIT_ID'] = 'visit_v0909'
        msg['JOB_NUM'] = 'job_100' 
        msg['ACK_ID'] = 'ack_100' 
        msg['REPLY_QUEUE'] = self.AR_FOREMAN_ACK_PUBLISH 
        final_target_location = self.archive_name + '@' + self.archive_ip + ":" +\
                                target_location 
        msg['TARGET_LOCATION'] = final_target_location
        xfer_params['RAFT_LIST'] = ['11']
        xfer_params['RAFT_CCD_LIST'] = 
        xfer_params['AR_FWDR'] = 
        msg['XFER_PARAMS'] = xfer_params 
        self.ar_publisher.publish_message('', msg) 

        msg['MSG_TYPE'] = 'AR_FWDR_HEALTH_CHECK'

        msg['MSG_TYPE'] = 'AR_FWDR_TAKE_IMAGES'

        msg['MSG_TYPE'] = 'AR_FWDR_HEADER_READY'
        msg['MSG_TYPE'] = 'AR_FWDR_END_READOUT'

        self.ar_publisher.publish_message(
        print("Message Sender Done.") 

    def verify_ocs_messages(self): 
        pass

    def clear_message_lists(self): 
        self.dmcs_consumer_msg_list = [] 

    def on_ocs_message(self, ch, method, properties, body): 
        pass
