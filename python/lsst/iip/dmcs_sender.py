import pika
#from FirehoseConsumer import FirehoseConsumer
from Consumer import Consumer
from SimplePublisher import SimplePublisher
import sys
import os
import time
import logging
import _thread
import toolsmod

class Premium:
  def __init__(self):
    logging.basicConfig()
    #os.system('rabbitmqctl -p /tester purge_queue firehose')
    #os.system('rabbitmqctl -p /tester purge_queue ack_publish')
    #broker_url = 'amqp://BASE:BASE@141.142.238.160:5672/%2Fbunny?heartbeat=300'
    broker_url = 'amqp://BASE:BASE@141.142.238.10:5672/%2Ftest'
    #pub_broker_url = 'amqp://BASE_PUB:BASE_PUB@141.142.238.160:5672/%2Fbunny'
    #broker_url = 'amqp://NCSA:NCSA@141.142.208.191:5672/%2Ftester'
    #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
    #self._cons = FirehoseConsumer(broker_url, 'firehose', "YAML")

    """
    self._cons = Consumer(broker_url, 'ar_foreman_consume', "YAML")
    try:
      _thread.start_new_thread( self.do_it, ("thread-1", 2,)  )
    except e:
      print("Cannot start thread")
      print(e)

    self._cons2 = Consumer(broker_url, 'pp_foreman_consume', "YAML")
    try:
      _thread.start_new_thread( self.do_it2, ("thread-3", 2,)  )
    except e:
      print("Cannot start thread")
      print(e)
    """
    cdm = toolsmod.intake_yaml_file("L1SystemCfg.yaml")
    self.ccd_list = cdm['ROOT']['CCD_LIST']
    
  def mycallback(self, ch, methon, properties, body):
    print("  ")
    print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<")
    print((" [z] body Received %r" % body))
    print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<")

    #print("Message done")
    #print("Still listening...")

  def mycallback2(self, ch, methon, properties, body):
    print("  ")
    print("++++++++++++++-----------+++++++++++++++")
    print((" [z] body Received %r" % body))
    print("++++++++++++++-----------+++++++++++++++")

    #print("Message done")
    #print("Still listening...")

  def do_it(self, threadname, delay):
    #example = ExampleConsumer('amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny')
    print("Before run call")
    self._cons.run(self.mycallback)
    print("After run call - not blocking")

  def do_it2(self, threadname, delay):
    #example = ExampleConsumer('amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny')
    print("Before run call")
    self._cons2.run(self.mycallback2)
    print("After run call - not blocking")

  

def main():
  premium = Premium()
  #sp1 = SimplePublisher('amqp://BASE_PUB:BASE_PUB@141.142.238.160:5672/%2Fbunny?heartbeat=300', "YAML")
  #sp1 = SimplePublisher('amqp://BASE_PUB:BASE_PUB@141.142.238.10:5672/%2Ftest', "YAML")
  sp1 = SimplePublisher('amqp://DMCS:DMCS@140.252.32.128:5672/%2Ftest_at', "YAML")
  #sp2 = SimplePublisher('amqp://TesT:TesT@141.142.208.191:5672/%2Ftester')
  #broker_url = 'amqp://FM:FM@141.142.238.160:5672/%2Fbunny'
  #cons = Consumer(broker_url, 'dmcs_ocs_publish')
  #try:
  #  thread.start_new_thread( do_it, ("thread-1", 2,)  )
  #except:
  #  print "Cannot start thread"


  #  while 1:

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

  msg = {}
  msg['MSG_TYPE'] = "DMCS_AT_START_INTEGRATION"
  msg['IMAGE_ID'] = 'AT_C_20180923_000050'
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
  msg['IMAGE_ID'] = 'AT_C_20180923_000050'
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
  msg["IMAGE_ID"] = 'AT_C_20180923_000050'
  msg["FILENAME"] = "http://localhost:8000/visitJune-28.header"
  time.sleep(4)
  sp1.publish_message("ocs_dmcs_consume", msg)

  time.sleep(5)

  print("Sender done")



if __name__ == "__main__":  main()
