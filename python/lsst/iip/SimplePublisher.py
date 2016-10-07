import pika
from pika.exceptions import *
import logging
import yaml
import sys
import toolsmod
from toolsmod import L1Exception
from toolsmod import L1MessageError
from XMLHandler import * 
from Exceptions import * 

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class SimplePublisher:

  EXCHANGE = 'message'

  def __init__(self, amqp_url):

    print "In SimplePublisher init, amqp_url is %s" % amqp_url
    self._connection = None
    self._channel = None
    self._message_number = 0
    self._stopping = False
    self._url = amqp_url
    self._closing = False
    self._xml_handler = None

    try:
       self.connect()
    except:
       LOGGER.error('No channel - connection channel is None')
       

  def connect(self):
    self._connection = pika.BlockingConnection(pika.URLParameters(self._url))
    self._channel = self._connection.channel()
    if self._channel == None:
      LOGGER.error('No channel - connection channel is None')

  def publish_message(self, route_key, msg):
    print "In SimplePublisher publish_message, amqp_url is %s and route_key is %s" % (self._url, route_key)
    #if self._channel.is_closed == True:
    if self._channel == None:
       try:
         self.connect()
       except AMQPError, e:
         print "e prints out as %s" % e 
         LOGGER.critical('Unable to create connection to rabbit server. Heading for exit...')
         sys.exit(105)

    LOGGER.debug ("Sending msg to %s", route_key)

    self._xml_handler = XMLHandler()
    try:
        xmlRoot = self._xml_handler.encodeXML(msg)
        valid = self._xml_handler.validate(xmlRoot)
        if valid: 
            xmlMsg = self._xml_handler.tostring(xmlRoot)
            self._channel.basic_publish(exchange=self.EXCHANGE, routing_key=route_key, body=xmlMsg)
        else: 
            raise L1MessageError("Message is invalid XML.")
    except L1MessageError, e:
        print("Error: %s" % e.errormsg)
        print "Message body to be published is: %s" % msg
        print "XML Version of message is %s" % xmlRoot
        raise L1MessageError("Message is invalid XML.")
