import pika
#from FirehoseConsumer import FirehoseConsumer
from lsst.ctrl.iip.Consumer import Consumer
from lsst.ctrl.iip.SimplePublisher import SimplePublisher
import sys
import os
import time
import logging
import _thread

class Premium:
  def __init__(self):
    logging.basicConfig()
    # commented out - srp
    #broker_url = 'amqp://FORWARD_F93:FORWARD_F93@140.252.32.128:5672/%2Ftest_at'
    broker_url = 'amqp://FORWARD_F93:FORWARD_F93@141.142.238.10:5672/%2Ftest_at_srp'

    #self.new_thread = Consumer(broker_url, 'telemetry_queue', 'xthread', self.mycallback, 'YAML')
    #self.new_thread.start()

    #cdm = toolsmod.intake_yaml_file("L1SystemCfg.yaml")
    #self.ccd_list = cdm['ROOT']['CCD_LIST']
   
  def mycallback(self, ch, method, properties, body):
    ch.basic_ack(method.delivery_tag)
    print("  ")
    print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<")
    print((" [z] body Received %r" % body))
    print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<")

    #print("Message done")
    #print("Still listening...")


def main():
  # commented out - srp
  #sp1 = SimplePublisher('amqp://DMCS:DMCS@140.252.32.128:5672/%2Ftest_at', "YAML")
  sp1 = SimplePublisher('amqp://DMCS:DMCS@141.142.238.10:5672/%2Ftest_at', "YAML")

  #while 1:
    #pass
  """
  """

  msg = {}
  msg['MSG_TYPE'] = "DMCS_AT_START_INTEGRATION"
  msg['IMAGE_ID'] = 'AT_O_20190315_000003'
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
  msg['IMAGE_ID'] = 'AT_O_20190315_000003'
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
  msg["IMAGE_ID"] = 'AT_O_20190315_000003'
  msg["FILENAME"] = "http://localhost:8000/visitJune-28.header"
  time.sleep(4)
  sp1.publish_message("ocs_dmcs_consume", msg)

  time.sleep(5)
  #print("Sender done")


  sp1.close()

if __name__ == "__main__":  main()
