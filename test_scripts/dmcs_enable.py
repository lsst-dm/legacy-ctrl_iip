import pika
from lsst.ctrl.iip.SimplePublisher import SimplePublisher
from lsst.ctrl.iip.Credentials import Credentials
import sys
import os
import time
import logging

if __name__ == "__main__":
    cred = Credentials('iip_cred.yaml')
    user = cred.getUser('service_user')
    passwd = cred.getPasswd('service_passwd')
  
    url = 'amqp://%s:%s@141.142.238.10:5672/%%2Ftest_at' % (user, passwd)
    sp1 = SimplePublisher(url, "YAML")

    """
    """
    msg = {}
    msg['MSG_TYPE'] = "STANDBY"
    msg['DEVICE'] = 'AT'
    #msg['CFG_KEY'] = "2C16"
    msg['ACK_ID'] = 'AT_4'
    msg['CMD_ID'] = '4434278812'
    time.sleep(3)
    print("AT STANDBY")
    sp1.publish_message("ocs_dmcs_consume", msg)

    msg = {}
    msg['MSG_TYPE'] = "DISABLE"
    msg['DEVICE'] = 'AT'
    msg['ACK_ID'] = 'AT_6'
    msg['CMD_ID'] = '4434278814'
    time.sleep(3)
    print("AT DISABLE")
    sp1.publish_message("ocs_dmcs_consume", msg)

    msg = {}
    msg['MSG_TYPE'] = "ENABLE"
    msg['DEVICE'] = 'AT'
    msg['ACK_ID'] = 'AT_11'
    msg['CMD_ID'] = '4434278816'
    time.sleep(3)
    print("AT ENABLE")
    sp1.publish_message("ocs_dmcs_consume", msg)

    sp1.close()
