# add path to PYTHONPATH
import sys
sys.path.insert(0, "/root/src/git/ctrl_iip/python/lsst/iip")

import pika 
from SimplePublisher import *
from toolsmod import * 
import time


publisher = SimplePublisher("amqp://ocs:ocs@141.142.208.241/%2fbunny")


def setup_queue(*queue_name): 
    connection = pika.BlockingConnection(pika.URLParameters("amqp://ocs:ocs@141.142.208.241/%2fbunny"))
    channel = connection.channel()

    channel.exchange_declare("message")
    for arg in queue_name: 
	channel.queue_declare(queue=arg)
	channel.queue_bind(queue=arg, exchange="message")
    connection.close() 

def send_ocs_dmcs(): 
    # BOOK_KEEPING
    msg = {} 
    msg["MSG_TYPE"] = "BOOK_KEEPING"
    msg["ACK_ID"] = "ENABLE_0000001"
    msg["ACK_DELAY"] = 2 # string 
    msg["TIME"] = get_timestamp()  # string  
    msg["CHECKBOX"] = False # string
    publisher.publish_message("DMCS_OCS_PUBLISH", msg)

    time.sleep(3)
    msg2 = {} 
    msg2["MSG_TYPE"] = "RESOLVE_ACK"
    publisher.publish_message("DMCS_OCS_PUBLISH", msg2) 
    
    
def main(): 
    # setup_queue("OCS_DMCS_CONSUME", "DMCS_OCS_PUBLISH")
    send_ocs_dmcs()

if __name__ == "__main__": main() 
