import sys
sys.path.insert(0, "/root/src/git/ctrl_iip/python/lsst/iip")

from Consumer import *
from SimplePublisher import * 
import yaml 

consumer = Consumer("amqp://ocs:ocs@141.142.208.241/%2fbunny", "OCS_DMCS_CONSUME")
publisher = SimplePublisher("amqp://ocs:ocs@141.142.208.241/%2fbunny")

def callback(ch, method, properties, body): 
    print "<<<< RUNNING <<<<<<"
    print body
    m = body
    
    msg = {} 
    msg["MSG_TYPE"] = m["MSG_TYPE"] + "_ACK"
    msg["DEVICE"] = m["DEVICE"] 
    msg["ACK_ID"] = m["ACK_ID"]
    msg["ACK_BOOL"] = "true"
    msg["ACK_STATEMENT"] = "everything works"
    msg["ACK_DELAY"] = str(m["ACK_DELAY"])
    msg["CMD_ID"] = m["CMD_ID"] 

    print msg
    publisher.publish_message("DMCS_OCS_PUBLISH", msg)

consumer.run(callback)
