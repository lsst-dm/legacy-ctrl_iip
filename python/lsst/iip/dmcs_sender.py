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
  sp1 = SimplePublisher('amqp://BASE_PUB:BASE_PUB@141.142.238.10:5672/%2Ftest', "YAML")
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

#  msg = {}
#  msg['MSG_TYPE'] = "STANDBY"
#  msg['DEVICE'] = 'PP'
#  msg['CFG_KEY'] = "2C16"
#  msg['ACK_ID'] = 'PP_7'
#  msg['ACK_DELAY'] = 2
#  msg['CMD_ID'] = '4434278813'
#  time.sleep(3)
#  print("PP STANDBY")
#  sp1.publish_message("ocs_dmcs_consume", msg)

  #msg = {}
  #msg['MSG_TYPE'] = "NEW_SESSION"
  #msg['SESSION_ID'] = 'SI_469976'
  #msg['ACK_ID'] = 'NEW_SESSION_ACK_44221'
  #msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
  ##time.sleep(3)
  ##sp1.publish_message("ar_foreman_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "DISABLE"
  msg['DEVICE'] = 'AT'
  msg['ACK_ID'] = 'AT_6'
  msg['CMD_ID'] = '4434278814'
  time.sleep(3)
  print("AT DISABLE")
  sp1.publish_message("ocs_dmcs_consume", msg)

#  msg = {}
#  msg['MSG_TYPE'] = "DISABLE"
#  msg['DEVICE'] = 'PP'
#  msg['ACK_ID'] = 'PP_8'
#  msg['ACK_DELAY'] = 2
#  msg['CMD_ID'] = '4434278815'
#  time.sleep(3)
#  print("PP DISABLE")
#  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "ENABLE"
  msg['DEVICE'] = 'AT'
  msg['ACK_ID'] = 'AT_11'
  msg['CMD_ID'] = '4434278816'
  time.sleep(3)
  print("AT ENABLE")
  sp1.publish_message("ocs_dmcs_consume", msg)

#  msg = {}
#  msg['MSG_TYPE'] = "ENABLE"
#  msg['DEVICE'] = 'PP'
#  msg['ACK_ID'] = 'PP_12'
#  msg['ACK_DELAY'] = 2
#  msg['CMD_ID'] = '4434278817'
#  time.sleep(3)
#  print("PP ENABLE")
#  sp1.publish_message("ocs_dmcs_consume", msg)


  """
  msg = {}
  msg['MSG_TYPE'] = "DISABLE"
  msg['DEVICE'] = 'AR'
  msg['ACK_ID'] = 'AR_10'
  msg['ACK_DELAY'] = 2
  time.sleep(5)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "ENABLE"
  msg['DEVICE'] = 'AR'
  msg['ACK_ID'] = 'AR_12'
  msg['ACK_DELAY'] = 2
  time.sleep(5)
  sp1.publish_message("ocs_dmcs_consume", msg)
  """ 
  """
  msg = {}
  msg['MSG_TYPE'] = "NEXT_VISIT"
  msg['VISIT_ID'] = 'V_1443'
  msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
  msg['ACK_ID'] = 'NEW_VISIT_ACK_76'
  msg['BORE_SIGHT'] = "231,123786456342, -45.3457156906, FK5"
  time.sleep(5)
  print("Next Visit Message")
  sp1.publish_message("ocs_dmcs_consume", msg)
  """
  msg = {}
  msg['MSG_TYPE'] = "DMCS_AT_START_INTEGRATION"
  msg['IMAGE_ID'] = 'LSSTTEST-01'
  msg['IMAGE_INDEX'] = 'MAIN'
  msg['VISIT_ID'] = 'V_1443'
  msg['ACK_ID'] = 'START_INT_ACK_76'
  msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
  msg['CCD_LIST'] = premium.ccd_list
  time.sleep(8)
  print("Start Integration Message")
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "DMCS_AT_END_READOUT"
  msg['VISIT_ID'] = 'V_1443'
  msg['IMAGE_ID'] = 'LSSTTEST-01'
  msg['IMAGE_INDEX'] = 'N'
  msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
  msg['ACK_ID'] = 'READOUT_ACK_77'
  time.sleep(5)
  print("READOUT Message")
  sp1.publish_message("ocs_dmcs_consume", msg)

  print("Sending HEADER1 information")
  msg = {}
  msg["MSG_TYPE"] = "DMCS_AT_HEADER_READY"
  msg["FILENAME"] = "felipe@141.142.238.177:/tmp/header/test23.header"
  time.sleep(4)
  sp1.publish_message("f99_consume", msg)

  """
  msg = {}
  msg['MSG_TYPE'] = "START_INTEGRATION"
  msg['IMAGE_ID'] = 'IMG_4277'
  msg['IMAGE_SRC'] = 'MAIN'
  msg['VISIT_ID'] = 'V_1443'
  msg['ACK_ID'] = 'START_INT_ACK_78'
  msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
  msg['CCD_LIST'] = premium.ccd_list
  time.sleep(5)
  print("Start Integration Message")
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "READOUT"
  msg['VISIT_ID'] = 'V_1443'
  msg['IMAGE_ID'] = 'IMG_4277'
  msg['IMAGE_SRC'] = 'MAIN'
  msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
  msg['ACK_ID'] = 'READOUT_ACK_79'
  time.sleep(5)
  print("READOUT Message")
  sp1.publish_message("ocs_dmcs_consume", msg)
  """
  time.sleep(15)

  print("Sender done")



if __name__ == "__main__":  main()
