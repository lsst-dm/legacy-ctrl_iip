import logging
logging.basicConfig(level=logging.ERROR)
import subprocess
import yaml
from Consumer import *
from SimplePublisher import *
from Helper import read_yaml
            
class RegisterMachine:
    """ Notes:
        callback_consumer: stop_consuming is a better method but Consumer doesn't let me do
    """ 
    INFO = None
    def __init__(self): 
        cfg = read_yaml("Registration.cfg") 
        self._broker_username = cfg["BROKER_USERNAME"] 
        self._broker_password = cfg["BROKER_PASSWORD"]
        self._broker_addr = cfg["BROKER_ADDR"] 
        self._publish_queue = cfg["PUBLISH_QUEUE"]
        self._consume_queue = cfg["CONSUME_QUEUE"] 
        self._amqpurl = "amqp://" + self._broker_username + ":" + self._broker_password + "@" + self._broker_addr
        self._hostname = self.get_hostname()
        self._ip_addr = self.get_ip_addr()
        self.setup_publisher()
        self.setup_consumer() 
    
    def setup_publisher(self): 
        self._publisher = SimplePublisher(self._amqpurl, formatOptions="yaml")

    def setup_consumer(self): 
        self._consumer = Consumer(self._amqpurl, self._consume_queue)

    def get_hostname(self): 
        # Remove the trailing \n
        hostname = subprocess.check_output(["hostname"], shell=False)[:-1]
        return hostname
        
    def get_ip_addr(self): 
        # Remove trailing \n and space
        ip_addr = subprocess.check_output(["hostname", "-I"], shell=False)[:-2]
        return ip_addr

    def publish_info(self): 
        machine_info = {}
        machine_info["MSG_TYPE"] = "REGISTERING_MACHINE"
        machine_info["HOSTNAME"] = self._hostname
        machine_info["IP_ADDR"] = self._ip_addr
        self._publisher.publish_message(self._publish_queue, yaml.dump(machine_info))
        print("[x] Message Sent.")
    
    def run_consumer(self): 
        self._consumer.run(self.callback_consumer)

    def callback_consumer(self, ch, method, properties, body): 
        SN = yaml.load(body)
        if (SN["IP_ADDR"] == self._ip_addr): 
            print("[x] Msg Received. %r" % body)
            self._consumer.acknowledge_message(method.delivery_tag)
            self.INFO = yaml.load(body)
            self._consumer.stop()
            self.send_ack()
    
    def send_ack(self): 
        ack = {}
        ack["MSG_TYPE"] = "REGISTRATION_COMPLETE_ACK"
        ack["FQN"] = self.INFO["FQN"]
        ack["IP_ADDR"] = self.INFO["IP_ADDR"]
        ack["HOSTNAME"] = self.INFO["HOSTNAME"]
        self._publisher.publish_message(self._publish_queue, yaml.dump(ack))
        print("[x] Ack Sent.")
        
    def return_listener(self): 
        return self.INFO

    def register(self): 
        self.publish_info()
        self.run_consumer() 
