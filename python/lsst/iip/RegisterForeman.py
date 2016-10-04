import threading
import subprocess
import random
import logging
from SimplePublisher import * 
from Consumer import * 
from Helper import read_yaml 

logging.basicConfig()
class RegisterForeman: 
    MACHINES = [] 
    SEED = 1

    def __init__(self, machineType, scoreboard): 
        cfg = read_yaml("Registration.cfg")
        self._broker_username = cfg["BROKER_USERNAME"]
        self._broker_password = cfg["BROKER_PASSWORD"]
        self._broker_addr = cfg["BROKER_ADDR"]
        self._publish_queue = cfg["CONSUME_QUEUE"]
        self._consume_queue = cfg["PUBLISH_QUEUE"]
        self._exchange = cfg["EXCHANGE"]
        self._amqpurl = "amqp://" + self._broker_username + ":" + self._broker_password + "@" + self._broker_addr
        self._machine_type = machineType
        self._scoreboard = scoreboard
        self._scoreboard_action = {"FORWARDER": self.set_forwarder_params, 
                                   "DISTRIBUTOR": self.set_distributor_params}
        self.setup_publisher()
        self.setup_consumer()

    def setup_publisher(self): 
        self._publisher = SimplePublisher(self._amqpurl, exchange=self._exchange, formatOptions="yaml")  

    def setup_consumer(self): 
        self._consumer = Consumer(self._amqpurl, self._consume_queue)
    
    def run_consumer(self): 
        self._consumer.run(self.callback_consumer) 
    
    def set_forwarder_params(self, forwarders, params):
        forwarder = []
        forwarder.append(forwarders) 
        self._scoreboard.set_forwarder_params(forwarder, params)

    def set_distributor_params(self, distributor, params):
        self._scoreboard.set_distributor_params(distributor, params)
        
    def callback_consumer(self, ch, method, properties, body): 
        print("[x] Message Received %r " % body)
        self._consumer.acknowledge_message(method.delivery_tag)
        msg = yaml.load(body)
        if msg["MSG_TYPE"] == "REGISTERING_MACHINE": 
            sqn = self.get_sequence_info(msg)
            params = { "STATE": "REGISTERING", "STATUS": "UNKNOWN" }
            params.update(sqn) # works as long as sqn does not contain STATE and STATUS fields
            action = self._scoreboard_action.get(self._machine_type)
            action(sqn["FQN"], params)
            self.publisher_info(sqn)
        elif msg["MSG_TYPE"] == "REGISTRATION_COMPLETE_ACK": 
            params = { "STATE": "HEALTHY", "STATUS": "IDLE" }
            action = self._scoreboard_action.get(self._machine_type)
            action( msg["FQN"], params)
            print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"

    def publisher_info(self, sequence_info): 
        print("[x] Sent message is %r"% yaml.dump(sequence_info))
        self.setup_account(sequence_info) 
        self._publisher.publish_message(self._publish_queue, yaml.dump(sequence_info))
        print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    
    def setup_account(self, body): 
        subprocess.call(["sudo", "rabbitmqctl", "add_user", body["USRNAME"], body["PASSWD"]])
        subprocess.call(["sudo", "rabbitmqctl", "set_permissions", "-p", "/bunny", body["USRNAME"], ".*", ".*", ".*"])

    def get_sequence_info(self, machine_info): 
        sequence_number = self.generate_random()
        account = self._machine_type[0] + "_" + str(sequence_number)
        SN = {}
        SN["FQN"] = self._machine_type + "_" + str(sequence_number)
        SN["CONSUME_QUEUE"] = self._machine_type[0] + str(sequence_number) + "_consume"
        SN["PUBLISH_QUEUE"] = self._machine_type.lower() + "_publish"
        SN["IP_ADDR"] = machine_info["IP_ADDR"]
        SN["USRNAME"] = account 
        SN["PASSWD"] = account
        SN["HOSTNAME"] = machine_info["HOSTNAME"] 
        return SN

    def generate_random_number(self, number): 
        if number not in self.MACHINES: 
            self.MACHINES.append(number)
            return number
        else: 
            number = random.randint(self.SEED, self.SEED+9)
            return self.generate_random_number(number)

    def generate_random(self): 
        if (self.SEED + 9 == len(self.MACHINES)):
            self.SEED = self.SEED + 10  
        return self.generate_random_number(1)
    
    def run(self): 
        self.run_consumer()
