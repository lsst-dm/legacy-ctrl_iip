import sys
sys.path.insert(0, "/root/src/git/ctrl_iip/python/lsst/iip")

from Consumer import *
from SimplePublisher import * 
import yaml 

consumer = Consumer("amqp://OCS:OCS@141.142.208.191/%2fbunny", "ocs_dmcs_consume")
publisher = SimplePublisher("amqp://OCS:OCS@141.142.208.191/%2fbunny")

def callback(ch, method, properties, body): 
    print("<<<< MESSAGE IS <<<<<<")
    print(body)
    m = body
    
    msg = {} 
    msg["MSG_TYPE"] = m["MSG_TYPE"] + "_ACK"
    msg["DEVICE"] = m["DEVICE"] 
    msg["ACK_ID"] = m["ACK_ID"]
    msg["ACK_BOOL"] = "true"
    msg["ACK_STATEMENT"] = "everything works"
    msg["CMD_ID"] = m["CMD_ID"] 

    print(msg)
    publisher.publish_message("dmcs_ocs_publish", msg)

print(">>> RUNNING <<<")
consumer.run(callback)
