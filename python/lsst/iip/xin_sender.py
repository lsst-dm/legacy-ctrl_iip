import pika
#from FirehoseConsumer import FirehoseConsumer
from .Consumer import Consumer
from .SimplePublisher import SimplePublisher
import sys
import os
import time
import logging
import _thread

class Premium:
  def __init__(self):
    logging.basicConfig()
    broker_url = 'amqp://BASE:BASE@141.142.238.160:5672/%2Fbunny?autoAck=true'
    self._cons = Consumer(broker_url, 'ocs_dmcs_consume', "YAML")
    try:
      _thread.start_new_thread( self.do_it, ("thread-1", 2,)  )
    except e:
      print("Cannot start thread")
      print(e)

    
  def mycallback(self, ch, methon, properties, body):
    print("  ")
    print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<")
    print((" [x] method Received %r" % methon))
    print((" [y] properties Received %r" % properties))
    print((" [z] body Received %r" % body))

    print("Message done")
    print("Still listening...")

  def do_it(self, threadname, delay):
    print("Before run call")
    self._cons.run(self.mycallback)
    print("After run call - not blocking")

  

def main():
  premium = Premium()
  sp1 = SimplePublisher('amqp://BASE:BASE@141.142.238.160:5672/%2Fbunny', "YAML")


  #  while 1:
  msg = {}
  msg['MSG_TYPE'] = "STANDBY"
  msg['DEVICE'] = 'AR'
  time.sleep(29)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "DISABLE"
  msg['DEVICE'] = 'AR'
  time.sleep(45)
  sp1.publish_message("ocs_dmcs_consume", msg)



  msg = {}
  msg['MSG_TYPE'] = "ENABLE"
  msg['DEVICE'] = 'AR'
  time.sleep(74)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "WORKING"
  msg['DEVICE'] = 'AR'
  time.sleep(150)
  sp1.publish_message("ocs_dmcs_consume", msg)

  time.sleep(5)



  print("Sender done")



if __name__ == "__main__":  main()
