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
  sp1 = SimplePublisher('amqp://PFM:PFM@141.142.238.10:5672/%2Ftest', "YAML")
  #sp1 = SimplePublisher('amqp://PFM:PFM@141.142.238.10:5672/%2Fbunny', "YAML")
  #sp2 = SimplePublisher('amqp://TesT:TesT@141.142.208.191:5672/%2Ftester')
  #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
  #cons = Consumer(broker_url, 'F8_consume')
  #try:
  #  thread.start_new_thread( do_it, ("thread-1", 2,)  )
  #except:
  #  print "Cannot start thread"


  print("Begin Send Messages...")

  print("Sending AR_FWDR_HEALTH_CHECK message")
  msg = {}
  msg['MSG_TYPE'] = "AR_FWDR_HEALTH_CHECK"
  msg['REPLY_QUEUE'] = 'ar_foreman_ack_publish'
  msg['ACK_ID'] = 'xxX22122'
  time.sleep(5)
  sp1.publish_message("f99_consume", msg)

  print("Sending AR_FWDR_XFER_PARAMS message")
  msg = {}
  msg['MSG_TYPE'] = "AR_FWDR_XFER_PARAMS"
  msg['JOB_NUM'] = 'j42'
  msg['TARGET_LOCATION'] = '/tmp/target'
  msg['SESSION_ID'] = 'sess77'
  msg['REPLY_QUEUE'] = 'ar_foreman_ack_publish'
  msg['DAQ_ADDR'] = 'LOCAL'
  msg['VISIT_ID'] = 'vv2'
  msg['ACK_ID'] = 'AR_FWDR_XFER_PARAMS_ACK_552'
  # These lists are prepped for sending directly to a forwarder
  msg["XFER_PARAMS"] = {}
  msg['XFER_PARAMS']['AR_FWDR'] = 'FORWARDER_F99'
  msg['XFER_PARAMS']['RAFT_LIST'] = ['raft01']
  #msg['XFER_PARAMS']['RAFT_CCD_LIST'] = [['11']]
  msg['XFER_PARAMS']['RAFT_CCD_LIST'] = [['ALL']]
  time.sleep(2)
  sp1.publish_message("f99_consume", msg)

  """
  print("Sending AR_FWDR_TAKE_IMAGES message")
  msg = {}
  msg['MSG_TYPE'] = "AR_FWDR_TAKE_IMAGES"
  msg['JOB_NUM'] = 'j42'
  msg['NUM_IMAGES'] = 2
  msg['REPLY_QUEUE'] = 'ar_foreman_ack_publish'
  msg['ACK_ID'] = 'AR_FWDR_TAKE_IMAGES_ACK_554'
  time.sleep(4)
  sp1.publish_message("f99_consume", msg)
  """
  print("Sending AR_FWDR_END_READOUT message")
  msg = {}
  msg['MSG_TYPE'] = "AR_FWDR_END_READOUT"
  #msg['IMAGE_ID'] = 'test23'
  #msg['IMAGE_ID'] = 'luckyme'
  msg['IMAGE_ID'] = 'RG'
  msg['JOB_NUM'] = 'j42'
  msg['VISIT_ID'] = 'vv2'
  msg['SESSION_ID'] = 'sess77'
  msg['REPLY_QUEUE'] = 'ar_foreman_ack_publish'
  msg['ACK_ID'] = 'AR_FWDR_END_READOUT_ACK_557'
  time.sleep(4)
  sp1.publish_message("f99_consume", msg)

  print("Sending HEADER1 information") 
  msg = {} 
  msg["MSG_TYPE"] = "FORMAT_HEADER_READY"
  msg['IMAGE_ID'] = 'RG'
  #msg["FILENAME"] = "felipe@141.142.237.177:/tmp/header/test23.header"
  #msg["FILENAME"] = "/tmp/source/header/luckyme/luckyme.header"
  msg["FILENAME"] = "/tmp/source/header/RG/RG.header"
  time.sleep(4)
  #sp1.publish_message("f99_consume", msg) 
  sp1.publish_message("format_consume_from_f99", msg) 

  """
  print("Sending HEADER2 information") 
  msg = {} 
  msg["MSG_TYPE"] = "AR_FWDR_HEADER_READY"
  msg["FILENAME"] = "felipe@141.142.237.177:/tmp/header/IMG_101.header"
  time.sleep(4)
  sp1.publish_message("f99_consume", msg) 

  print("Sending AR_FWDR_END_READOUT message")
  msg = {}
  msg['MSG_TYPE'] = "AR_FWDR_END_READOUT"
  #msg['IMAGE_ID'] = 'test25'
  msg['IMAGE_ID'] = 'LSSTTEST_02'
  msg['JOB_NUM'] = 'j42'
  msg['VISIT_ID'] = 'vv2'
  msg['SESSION_ID'] = 'sess77'
  msg['REPLY_QUEUE'] = 'ar_foreman_ack_publish'
  msg['ACK_ID'] = 'AR_FWDR_END_READOUT_ACK_558'
  time.sleep(4)
  sp1.publish_message("f99_consume", msg)

  print("Sending AR_FWDR_TAKE_IMAGES_DONE message")
  msg = {}
  msg['MSG_TYPE'] = "AR_TAKE_IMAGES_DONE"
  msg['JOB_NUM'] = 'j42'
  msg['REPLY_QUEUE'] = 'ar_foreman_ack_publish'
  msg['ACK_ID'] = 'AR_FWDR_TAKE_IMAGES_ACK_554'
  time.sleep(6)
  sp1.publish_message("f99_consume", msg)
  """
  print("Sender done")
  


if __name__ == "__main__":  main()
