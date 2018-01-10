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
    #broker_url = 'amqp://BASE:BASE@141.142.238.160:5672/%2Fbunny?heartbeat=300'
    broker_url = 'amqp://DMCS_PUB:DMCS_PUB@141.142.238.10:5672/%2Ftest'
    #broker_url = 'amqp://NCSA:NCSA@141.142.208.191:5672/%2Ftester'
    #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
    #self._cons = FirehoseConsumer(broker_url, 'firehose', "YAML")
    """
    self._cons = Consumer(broker_url, 'ocs_dmcs_consume', "YAML")
    try:
      _thread.start_new_thread( self.do_it, ("thread-1", 2,)  )
    except e:
      print("Cannot start thread")
      print(e)

    time.sleep(2)
    """
    
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
  sp1 = SimplePublisher('amqp://DMCS_PUB:DMCS_PUB@141.142.238.10:5672/%2Ftest', "YAML")
  #sp1 = SimplePublisher('amqp://BASE:BASE@141.142.238.160:5672/%2Fbunny', "YAML")
  #sp2 = SimplePublisher('amqp://TesT:TesT@141.142.208.191:5672/%2Ftester')
  #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
  #cons = Consumer(broker_url, 'F8_consume')
  #try:
  #  thread.start_new_thread( do_it, ("thread-1", 2,)  )
  #except:
  #  print "Cannot start thread"


  #  while 1:
  msg = {}
  msg['MSG_TYPE'] = "FETCH_HEALTH_CHECK"
  msg['DEVICE'] = 'AR'
  time.sleep(2)
  sp1.publish_message("fetch_consume_from_f1", msg)

  msg = {}
  msg['MSG_TYPE'] = "SP_FETCH"
  msg['DEVICE'] = 'AR'
  time.sleep(2)
  sp1.publish_message("fetch_consume_from_f1", msg)

  msg = {}
  msg['MSG_TYPE'] = "PP_FORMAT"
  msg['DEVICE'] = 'AR'
  time.sleep(4)
  sp1.publish_message("format_consume_from_f1", msg)

  msg = {}
  msg['MSG_TYPE'] = "FORWARD_HEALTH_CHECK"
  msg['DEVICE'] = 'AR'
  time.sleep(1)
  sp1.publish_message("forward_consume_from_f1", msg)

  msg = {}
  msg['MSG_TYPE'] = "SP_FORWARD"
  msg['DEVICE'] = 'AR'
  time.sleep(1)
  sp1.publish_message("forward_consume_from_f1", msg)

  msg = {}
  msg['MSG_TYPE'] = "AR_FORWARD_ACK"
  msg['DEVICE'] = 'AR'
  time.sleep(1)
  sp1.publish_message("f1_consume_from_forwarder", msg)

  msg = {}
  msg['MSG_TYPE'] = "FORMAT_HEALTH_CHECK_ACK"
  msg['DEVICE'] = 'AR'
  time.sleep(1)
  sp1.publish_message("f1_consume_from_format", msg)

  msg = {}
  msg['MSG_TYPE'] = "PP_FETCH_ACK"
  msg['DEVICE'] = 'AR'
  time.sleep(1)
  sp1.publish_message("f1_consume_from_fetch", msg)

  msg = {}
  msg['MSG_TYPE'] = "PP_TAKE_IMAGE"
  msg['DEVICE'] = 'AR'
  time.sleep(1)
  sp1.publish_message("f1_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "AR_END_READOUT"
  msg['DEVICE'] = 'AR'
  time.sleep(1)
  sp1.publish_message("f1_consume", msg)

  time.sleep(5)


  """
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
