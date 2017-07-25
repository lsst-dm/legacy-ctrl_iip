import pika
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
    broker_url = 'amqp://BASE:BASE@141.142.238.160:5672/%2Fbunny'
    #broker_url = 'amqp://NCSA:NCSA@141.142.208.191:5672/%2Ftester'
    #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
    #self._cons = FirehoseConsumer(broker_url, 'firehose', "YAML")
    self._cons = Consumer(broker_url, 'f1_consume', "YAML")
    #self._cons = Consumer(broker_url, 'pp_foreman_consume', "YAML")
    self._cons2 = Consumer(broker_url, 'ncsa_consume', "YAML")
    try:
      _thread.start_new_thread( self.do_it, ("thread-1", 2,)  )
    except e:
      print("Cannot start thread")
      print(e)
    
    try:
      _thread.start_new_thread( self.do_it2, ("thread-2", 2,)  )
    except e:
      print("Cannot start thread")
      print(e)
    
  def mycallback(self, ch, methon, properties, body):
    print("  ")
    print("+++++++++++++=========++++++++++++++++")
    print(" f1_consume msg:")
    print(body)


  def mycallback2(self, ch, methon, properties, body):
    print("  ")
    print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<")
    print(" f2_consume msg:")
    print(body)


  def do_it(self, threadname, delay):
    print("Before run call")
    self._cons.run(self.mycallback)

  def do_it2(self, threadname, delay):
    print("Before run call")
    self._cons2.run(self.mycallback2)

  

def main():
  premium = Premium()
  sp1 = SimplePublisher('amqp://BASE_PUB:BASE_PUB@141.142.238.160:5672/%2Fbunny', "YAML")
  #sp2 = SimplePublisher('amqp://TesT:TesT@141.142.208.191:5672/%2Ftester')
  #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
  #cons = Consumer(broker_url, 'F8_consume')
  #try:
  #  thread.start_new_thread( do_it, ("thread-1", 2,)  )
  #except:
  #  print "Cannot start thread"


  #  while 1:
#  msg = {}
#  msg['MSG_TYPE'] = 'NEW_ARCHIVE_ITEM'
#  msg['SESSION_ID'] = "Tues_xx417"
#  msg['VISIT_ID'] = "V_5512"
#  msg['IMAGE_TYPE'] = 'AR'
#  msg['IMAGE_ID'] = "IMG_442"
#  msg['ACK_ID'] = "NEW_ITEM_ACK_14"
#  time.sleep(3)
#  sp1.publish_message("archive_ctrl_consume", msg)

  #msg = {}
  #msg['MSG_TYPE'] = "DISABLE"
  #msg['DEVICE'] = 'AR'
  #time.sleep(5)
  #sp1.publish_message("ocs_dmcs_consume", msg)

  #msg = {}
  #msg['MSG_TYPE'] = 'AR_ITEMS_XFERD'
  #msg['IMAGE_ID'] = "IMG_442"
  #msg['CCD_LIST'] = {'4':{ 'FILENAME':'/mnt/xfer_dir/101_100_4.fits','CHECKSUM':'348e1dbe4956e9d8d2dfa97535744561'}}
  #msg['ACK_ID'] = 'AR_ITEMS_ACK_2241'
  #time.sleep(5)
  #sp1.publish_message("archive_ctrl_consume", msg)

  
  msg = {}
  msg['MSG_TYPE'] = "NEW_SESSION"
  msg['SESSION_ID'] = 'session_RZ_22'
  msg['RESPONSE_QUEUE'] = 'dmcs_consume'
  msg['ACK_ID'] = 'NEW_SESSION_ACK_14'
  time.sleep(4)
  sp1.publish_message("pp_foreman_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "NEXT_VISIT"
  msg['SESSION_ID'] = 'session_RZ_22'
  msg['VISIT_ID'] = 'XX_28272'
  msg['BORE_SIGHT'] = 'A LITTLE TO THE LEFT'
  msg['RESPONSE_QUEUE'] = 'dmcs_consume'
  msg['ACK_ID'] = 'NEXT_VISIT_ACK_15'
  time.sleep(4)
  sp1.publish_message("pp_foreman_consume", msg)

  msg = {}
  msg['MSG_TYPE'] = "START_INTEGRATION"
  msg['JOB_NUM'] = '121163'
  msg['IMAGE_ID'] = 'IMG_444244'
  msg['VISIT_ID'] = 'VV1X004'
  msg['RESPONSE_QUEUE'] = 'dmcs_ack_consume'
  time.sleep(4)
  sp1.publish_message("pp_foreman_consume", msg)
  time.sleep(14)

  #msg = {}
  #msg['MSG_TYPE'] = "READOUT"
  #msg['IMAGE_ID'] = 'IMG_444244'
  #msg['DEVICE'] = 'AR'
  #time.sleep(4)
  #sp1.publish_message("ocs_dmcs_consume", msg)
 

  print("Sender done")


    #sp2.publish_message("ack_publish", "No, It's COLD")
    #time.sleep(2)
    #pass



if __name__ == "__main__":  main()
