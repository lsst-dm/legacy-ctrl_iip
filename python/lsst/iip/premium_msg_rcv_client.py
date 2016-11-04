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
    os.system('rabbitmqctl -p /tester purge_queue firehose')
    os.system('rabbitmqctl -p /tester purge_queue ack_publish')
    broker_url = 'amqp://TesT:TesT@141.142.208.191:5672/%2Ftester'
    #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
    #self._cons = FirehoseConsumer(broker_url, 'firehose', "YAML")
    self._cons = Consumer(broker_url, 'ack_publish', "YAML")
    try:
      thread.start_new_thread( self.do_it, ("thread-1", 2,)  )
    except e:
      print "Cannot start thread"
      print e
    
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
  sp1 = SimplePublisher('amqp://TesT:TesT@141.142.208.191:5672/%2Ftester')
  sp2 = SimplePublisher('amqp://TesT:TesT@141.142.208.191:5672/%2Ftester')
  #broker_url = 'amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny'
  #cons = Consumer(broker_url, 'F8_consume')
  #try:
  #  thread.start_new_thread( do_it, ("thread-1", 2,)  )
  #except:
  #  print "Cannot start thread"


  while 1:
    #sp1.publish_message("ack_publish", "It's hot")
    #time.sleep(2)
    #sp2.publish_message("ack_publish", "No, It's COLD")
    #time.sleep(2)
    pass

if __name__ == "__main__":  main()
