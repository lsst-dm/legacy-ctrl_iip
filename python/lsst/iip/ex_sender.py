import pika
#from FirehoseConsumer import FirehoseConsumer
from Consumer import Consumer
from SimplePublisher import SimplePublisher
import sys
import os
import time
import logging
import _thread

class Premium:
  def __init__(self):
    logging.basicConfig()
    #os.system('rabbitmqctl -p /tester purge_queue firehose')
    #os.system('rabbitmqctl -p /tester purge_queue ack_publish')
    #broker_url = 'amqp://BASE:BASE@141.142.208.191:5672/%2Fbunny'
    #broker_url = 'amqp://BASE:BASE@141.142.238.160:5672/%2Fbunny?heartbeat=300'
    #broker_url = 'amqp://PFM:PFM@141.142.238.10:5672/%2Fbunny?autoAck=true'
    #broker_url = 'amqp://NCSA:NCSA@141.142.208.191:5672/%2Ftester'
    #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
    #self._cons = FirehoseConsumer(broker_url, 'firehose', "YAML")
    #self._cons = Consumer(broker_url, 'ocs_dmcs_consume', "YAML")
    #try:
    #  _thread.start_new_thread( self.do_it, ("thread-1", 2,)  )
    #except e:
    #  print("Cannot start thread")
    #  print(e)

    #time.sleep(420)
    
  def mycallback(self, ch, methon, properties, body):
    print("  ")
    print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<")
    print((" [x] method Received %r" % methon))
    print((" [y] properties Received %r" % properties))
    print((" [z] body Received %r" % body))

    print("Message done")
    print("Still listening...")

  def do_it(self, threadname, delay):
    #example = ExampleConsumer('amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny')
    print("Before run call")
    self._cons.run(self.mycallback)
    print("After run call - not blocking")

  

def main():
  premium = Premium()
  #sp1 = SimplePublisher('amqp://BASE:BASE@141.142.238.160:5672/%2Fbunny?heartbeat=300', "YAML")
  sp1 = SimplePublisher('amqp://PFM:PFM@141.142.238.10:5672/%2Fbunny', "YAML")
  #sp2 = SimplePublisher('amqp://TesT:TesT@141.142.208.191:5672/%2Ftester')
  #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
  #cons = Consumer(broker_url, 'F8_consume')
  #try:
  #  thread.start_new_thread( do_it, ("thread-1", 2,)  )
  #except:
  #  print "Cannot start thread"


  time.sleep(3)
  #  while 1:
  msg = {}
  msg['MSG_TYPE'] = "DO_SOMETHING"
  msg['RAFT_LIST'] = {'01','11','31','40'}
  time.sleep(2)
  sp1.publish_message("ocs_dmcs_consume", msg)

  """
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


  msg = {}
  msg['MSG_TYPE'] = "NEXT_VISIT"
  msg['VISIT_ID'] = 'XX_28272'
  msg['BORE_SIGHT'] = 'A LITTLE TO THE LEFT'
  time.sleep(4)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "START_INTEGRATION"
  msg['IMAGE_ID'] = 'IMG_444244'
  msg['DEVICE'] = 'AR'
  time.sleep(4)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "READOUT"
  msg['IMAGE_ID'] = 'IMG_444244'
  msg['DEVICE'] = 'AR'
  time.sleep(4)
  sp1.publish_message("ocs_dmcs_consume", msg)
  """ 

  print("Sender done")


    #sp2.publish_message("ack_publish", "No, It's COLD")
    #time.sleep(2)
    #pass









if __name__ == "__main__":  main()
