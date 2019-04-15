import pika
from lsst.ctrl.iip.Credentials import Credentials
from lsst.ctrl.iip.SimplePublisher import SimplePublisher
import sys
import os
import time
import logging
import _thread

if __name__ == "__main__":
    cred = Credentials('iip_cred.yaml')
    user = cred.getUser('service_user')
    passwd = cred.getPasswd('service_passwd')

    url = 'amqp://%s:%s@141.142.238.10:5672/%%2Ftest_at' % (user, passwd)
    sp1 = SimplePublisher(url, "YAML")

    """
    """
  
    msg = {}
    msg['MSG_TYPE'] = "DMCS_AT_START_INTEGRATION"
    msg['IMAGE_ID'] = 'AT_O_20190315_000003'
    msg['IMAGE_INDEX'] = '2'
    msg['IMAGE_SEQUENCE_NAME'] = 'MAIN'
    msg['IMAGES_IN_SEQUENCE'] = '3'
    msg['ACK_ID'] = 'START_INT_ACK_76'
    msg['REPLY_QUEUE'] = "dmcs_ack_consume"
    time.sleep(8)
    print("Start Integration Message")
    sp1.publish_message("ocs_dmcs_consume", msg)
  
    msg = {}
    msg['MSG_TYPE'] = "DMCS_AT_END_READOUT"
    msg['IMAGE_ID'] = 'AT_O_20190315_000003'
    msg['IMAGE_INDEX'] = '2'
    msg['IMAGE_SEQUENCE_NAME'] = 'MAIN'
    msg['IMAGES_IN_SEQUENCE'] = '3'
    msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
    msg['ACK_ID'] = 'READOUT_ACK_77'
    time.sleep(5)
    print("READOUT Message")
    sp1.publish_message("ocs_dmcs_consume", msg)
  
    print("Sending HEADER1 information")
    msg = {}
    msg["MSG_TYPE"] = "DMCS_AT_HEADER_READY"
    msg["IMAGE_ID"] = 'AT_O_20190315_000003'
    msg["FILENAME"] = "http://localhost:8000/visitJune-28.header"
    time.sleep(4)
    sp1.publish_message("ocs_dmcs_consume", msg)
  
    time.sleep(5)
    #print("Sender done")
  
  
    sp1.close()
  
