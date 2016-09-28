import pika 
from XMLHandler import *

class Consumer(object): 
    
    def __init__(self, amqp_url, queue, exchange_name="message", exchange_type="direct", format_options=None): 
        self._connection = None
        self._channel = None 
        self._amqp_url = amqp_url
        self._queue = queue
        self._exchange_name = exchange_name
        self._exchange_type = exchange_type 
        self._format_options = format_options
        self._xml_handler = None 
        self._message_callback = None

    def connect(self): 
        self._connection = pika.SelectConnection(pika.URLParameters(self._amqp_url))
        self._channel = self._connection.channel()
    
    def setup_exchange(self, exchange_name): 
        self._channel.exchange_declare(exchange=self._exchange_name,
                                       exchange_type=self._exchange_type)

    def setup_queue(self): 
        self._channel.queue_declare(queue=self._queue)

    def setup_queue_binding(self): 
        self._channel.queue_bind(queue=self._queue,
                                 exchange=self._exchange_name)

    def start_consuming(self): 
        self._channel.basic_consume(self._message_callback, self._queue)

    def stop_consuming(self): 
        self._channel.stop_consuming()

    def close_channel(self): 
        self._channel.close() 

    def close_connection(self): 
        self._connection.close() 

    def run(self, callback): 
        if self._format_options == "XML": 
            self._xml_handler = XMLHandler(callback)
            self._message_callback = self._xml_handler.xmlcallback
        else: 
            self._message_callback = callback 
        self._connection = self.connect()
        self.setup_exchange()
        self.setup_queue()
        self.setup_queue_binding() 
        self.start_consuming()
        self._connection.ioloop.start()
