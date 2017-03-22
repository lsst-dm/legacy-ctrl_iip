import pika
#from FirehoseConsumer import FirehoseConsumer
from Consumer import Consumer
from SimplePublisher import SimplePublisher
import sys
import os
import time
import logging
import thread
import toolsmod

class Premium:
  def __init__(self):
    logging.basicConfig()
    #os.system('rabbitmqctl -p /tester purge_queue firehose')
    #os.system('rabbitmqctl -p /tester purge_queue ack_publish')
    broker_url = 'amqp://BASE:BASE@141.142.238.160:5672/%2Fbunny'
    pub_broker_url = 'amqp://BASE_PUB:BASE_PUB@141.142.238.160:5672/%2Fbunny'
    #broker_url = 'amqp://NCSA:NCSA@141.142.208.191:5672/%2Ftester'
    #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
    #self._cons = FirehoseConsumer(broker_url, 'firehose', "YAML")
    self._cons = Consumer(broker_url, 'dmcs_ocs_publish', "YAML")
    try:
      thread.start_new_thread( self.do_it, ("thread-1", 2,)  )
    except e:
      print "Cannot start thread"
      print e
    cdm = toolsmod.intake_yaml_file("L1SystemCfg.yaml")
    self.ccd_list = cdm['ROOT']['CCD_LIST']
    
  def mycallback(self, ch, methon, properties, body):
    print "  "
    print ">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<"
    print(" [x] method Received %r" % methon)
    print(" [y] properties Received %r" % properties)
    print(" [z] body Received %r" % body)

    print("Message done")
    print("Still listening...")

  def do_it(self, threadname, delay):
    #example = ExampleConsumer('amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny')
    print "Before run call"
    self._cons.run(self.mycallback)
    print "After run call - not blocking"

  

def main():
  premium = Premium()
  sp1 = SimplePublisher('amqp://BASE_PUB:BASE_PUB@141.142.238.160:5672/%2Fbunny', "YAML")
  #sp2 = SimplePublisher('amqp://TesT:TesT@141.142.208.191:5672/%2Ftester')
  #broker_url = 'amqp://FM:FM@141.142.238.160:5672/%2Fbunny'
  #cons = Consumer(broker_url, 'dmcs_ocs_publish')
  #try:
  #  thread.start_new_thread( do_it, ("thread-1", 2,)  )
  #except:
  #  print "Cannot start thread"


  #  while 1:

  msg = {}
  msg['MSG_TYPE'] = "NEW_SESSION"
  msg['SESSION_ID'] = 'SI_469976'
  msg['ACK_ID'] = 'NEW_SESSION_ACK_44221'
  msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
  #time.sleep(3)
  #sp1.publish_message("ar_foreman_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "NEXT_VISIT"
  msg['VISIT_ID'] = 'V_1443'
  msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
  msg['ACK_ID'] = 'NEW_VISIT_ACK_76'
  msg['BORE_SIGHT'] = "Up a little more...now back"
  #time.sleep(4)
  #sp1.publish_message("ar_foreman_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "START_INTEGRATION"
  msg['JOB_NUM'] = 'JAR_66756'
  msg['IMAGE_ID'] = 'IMG_4276'
  msg['IMAGE_SRC'] = 'MAIN'
  msg['SESSION_ID'] = 'SI_469976'
  msg['VISIT_ID'] = 'V_1443'
  msg['ACK_ID'] = 'START_INT_ACK_77'
  msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
  msg['CCD_LIST'] = premium.ccd_list
  #time.sleep(7)
  #sp1.publish_message("ar_foreman_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "READOUT"
  msg['JOB_NUM'] = 'JAR_66756'
  msg['SESSION_ID'] = 'SI_469976'
  msg['VISIT_ID'] = 'V_1443'
  msg['IMAGE_ID'] = 'IMG_444244'
  msg['IMAGE_SRC'] = 'MAIN'
  msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
  msg['ACK_ID'] = 'READOUT_ACK_78'
  #time.sleep(1)
  #sp1.publish_message("ar_foreman_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "STANDBY"
  msg['DEVICE'] = 'AR'
  msg['CFG_KEY'] = "2C16"
  msg['ACK_ID'] = 'AR_4'
  msg['ACK_DELAY'] = 2
  time.sleep(3)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "DISABLE"
  msg['DEVICE'] = 'AR'
  msg['ACK_ID'] = 'AR_6'
  msg['ACK_DELAY'] = 2
  time.sleep(3)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "ENABLE"
  msg['DEVICE'] = 'AR'
  msg['ACK_ID'] = 'AR_8'
  msg['ACK_DELAY'] = 2
  time.sleep(3)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "DISABLE"
  msg['DEVICE'] = 'AR'
  msg['ACK_ID'] = 'AR_10'
  msg['ACK_DELAY'] = 2
  time.sleep(3)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "ENABLE"
  msg['DEVICE'] = 'AR'
  msg['ACK_ID'] = 'AR_12'
  msg['ACK_DELAY'] = 2
  time.sleep(3)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "STANDBY"
  msg['DEVICE'] = 'AR'
  msg['CFG_KEY'] = "5A11"
  msg['ACK_ID'] = 'AR_14'
  msg['ACK_DELAY'] = 2
  time.sleep(3)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "ENABLE"
  msg['DEVICE'] = 'AR'
  msg['ACK_ID'] = 'AR_16'
  msg['ACK_DELAY'] = 2
  time.sleep(3)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "DISABLE"
  msg['DEVICE'] = 'AR'
  msg['CFG_KEY'] = "1A44"
  msg['ACK_ID'] = 'AR_18'
  msg['ACK_DELAY'] = 2
  time.sleep(3)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "FINAL"
  msg['DEVICE'] = 'AR'
  msg['ACK_ID'] = 'AR_20'
  msg['ACK_DELAY'] = 2
  time.sleep(3)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "STANDBY"
  msg['CFG_KEY'] = "7C17"
  msg['DEVICE'] = 'AR'
  msg['ACK_ID'] = 'AR_22'
  msg['ACK_DELAY'] = 2
  time.sleep(3)
  sp1.publish_message("ocs_dmcs_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "OFFLINE"
  msg['DEVICE'] = 'AR'
  msg['ACK_ID'] = 'AR_24'
  msg['ACK_DELAY'] = 2
  time.sleep(3)
  sp1.publish_message("ocs_dmcs_consume", msg)

  time.sleep(4)

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

  print "Sender done"


    #sp2.publish_message("ack_publish", "No, It's COLD")
    #time.sleep(2)
    #pass









if __name__ == "__main__":  main()
