import pika
from FirehoseConsumer import FirehoseConsumer
from Consumer import Consumer
from SimplePublisher import SimplePublisher
import sys
import os
import time
import logging
import thread

class Premium:
  def __init__(self):
    logging.basicConfig()
    #os.system('rabbitmqctl -p /tester purge_queue firehose')
    #os.system('rabbitmqctl -p /tester purge_queue ack_publish')
    broker_url = 'amqp://BASE:BASE@141.142.208.191:5672/%2Fbunny'
    #broker_url = 'amqp://NCSA:NCSA@141.142.208.191:5672/%2Ftester'
    #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
    #self._cons = FirehoseConsumer(broker_url, 'firehose', "YAML")
    #self._cons = Consumer(broker_url, 'ar_foreman_consume', "YAML")
    #try:
    #  thread.start_new_thread( self.do_it, ("thread-1", 2,)  )
    #except e:
    #  print "Cannot start thread"
    #  print e
    
  def mycallback(self, ch, methon, properties, body):
    ch.basic_ack(methon.delivery_tag) 
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
  sp1 = SimplePublisher('amqp://BASE:BASE@141.142.208.191:5672/%2Fbunny', "YAML")
  #sp2 = SimplePublisher('amqp://TesT:TesT@141.142.208.191:5672/%2Ftester')
  #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
  #cons = Consumer(broker_url, 'F8_consume')
  #try:
  #  thread.start_new_thread( do_it, ("thread-1", 2,)  )
  #except:
  #  print "Cannot start thread"


  #  while 1:
  msg = {}
  msg['MSG_TYPE'] = "FORWARDER_HEALTH_CHECK"
  msg['ACK_ID'] = 'AR_FWD_HEALTH_ACK_1662'
  msg['REPLY_QUEUE'] = 'ar_foreman_ack_publish'
  time.sleep(3)
  sp1.publish_message("f1_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "AR_XFER_PARAMS"
  msg['JOB_NUM'] = "j_1412_z"
  msg['VISIT_ID'] = 'V229'
  msg['IMAGE_ID'] = 'IMG_226XT_46'
  msg['ACK_ID'] = 'AR_XFER_PARAMS_ACK_112'
  msg['TARGET_DIR'] = "/mnt/xfer_dir/"
  msg['REPLY_QUEUE'] = 'ar_foreman_ack_publish'
  m = {}
  m['CCD_LIST'] = ['1','6','2','3','9','4','7','8']
  m['XFER_UNIT'] = ['CCD']
  m['FQN'] = 'ARCHIVE'
  m['NAME'] = "archive"
  m['HOSTNAME'] = 'blarg'
  m['IP_ADDR'] = '141.142.210.202'
  m['IMG_SRC'] = "blah"  # For future use...
  msg['XFER_PARAMS'] = m
  time.sleep(3)
  sp1.publish_message("f1_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "AR_READOUT"
  msg['JOB_NUM'] = "j_1412_z"
  msg['IMAGE_ID'] = 'IMG_226XT_46'
  msg['ACK_ID'] = 'AR_READOUT_ACK_92112'
  msg['REPLY_QUEUE'] = 'ar_foreman_ack_publish'
  time.sleep(4)
  sp1.publish_message("f1_consume", msg)


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
