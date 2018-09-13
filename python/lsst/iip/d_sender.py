import pika
#from FirehoseConsumer import FirehoseConsumer
from Consumer import Consumer
from SimplePublisher import SimplePublisher
import sys
import os
import time
import logging
import threading
import toolsmod

class Premium:
  def __init__(self):
    logging.basicConfig()
    broker_url = 'amqp://DMCS:DMCS@141.142.238.10:5672/%2Ftest'

    self.new_thread = Consumer(broker_url, 'dmcs_ocs_publish', 'xthread', self.mycallback, 'YAML')
    self.new_thread.start()
    
  def mycallback(self, ch, method, properties, body):
    ch.basic_ack(method.delivery_tag)
    print("  ")
    print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<")
    print((" [z] body Received %r" % body))
    print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<")

    #print("Message done")
    #print("Still listening...")

  

def main():
  premium = Premium()
  sp1 = SimplePublisher('amqp://DMCS_PUB:DMCS_PUB@141.142.238.10:5672/%2Ftest', "YAML")

  time.sleep(3)

  #  while 1:

  msg = {}
  msg['MSG_TYPE'] = "REQUEST_ACK_ID"
  msg['REPLY_QUEUE'] = 'DMCS_OCS_PUBLISH'
  sp1.publish_message("gen_dmcs_consume", msg)

  time.sleep(1)
  print("Sender done")



if __name__ == "__main__":  main()
