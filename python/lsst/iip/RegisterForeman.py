import subprocess
import random
import logging
from SimplePublisher import * 
from Consumer import * 

logging.basicConfig()
class RegisterForeman: 
    BROKER_USRNAME = "NCSA_FM"
    BROKER_PASSWD = "NCSA_FM"
    BROKER_ADDR = "141.142.208.241/%2fregi"
    CONSUME_QUEUE = "registering_machine"
    PUBLISH_QUEUE = "responding_ack"
    EXCHANGE = "register_msg"
    MACHINES = [] 
    SEED = 1

    def __init__(self, machineType, scoreboard): 
        self._broker_username = self.BROKER_USRNAME
        self._broker_password = self.BROKER_PASSWD
        self._broker_addr = self.BROKER_ADDR
        self._amqpurl = "amqp://" + self._broker_username + ":" + self._broker_password + "@" + self._broker_addr
        self._machine_type = machineType
        self._scoreboard = scoreboard
        self._scoreboard_action = {"FORWARDER": self.set_forwarder_params, 
                                   "DISTRIBUTOR": self.set_distributor_params}
        self.setup_publisher()
        self.setup_consumer()

    def setup_publisher(self): 
        self._publisher = SimplePublisher(self._amqpurl, exchange=self.EXCHANGE, formatOptions="yaml")  

    def setup_consumer(self): 
        self._consumer = Consumer(self._amqpurl, self.CONSUME_QUEUE)
    
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
        sqn = self.get_sequence_info(body)
        params = { "STATE": "REGISTERING", "STATUS": "UNKNOWN" }
        params.update(sqn) # works as long as sqn does not contain STATE and STATUS fields
        action = self._scoreboard_action.get(self._machine_type)
        action(sqn["FQN"], params)
        self.publisher_info(sqn)

    def publisher_info(self, sequence_info): 
        print("[x] Sent message is %r"% yaml.dump(sequence_info))
        self.setup_account(sequence_info) 
        self._publisher.publish_message(self.PUBLISH_QUEUE, yaml.dump(sequence_info))
        print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    
    def setup_account(self, body): 
        subprocess.call(["sudo", "rabbitmqctl", "add_user", body["USRNAME"], body["PASSWD"]])
        subprocess.call(["sudo", "rabbitmqctl", "set_permissions", "-p", "/bunny", body["USRNAME"], ".*", ".*", ".*"])

    def get_sequence_info(self, machine_info): 
        machine_info = yaml.load(machine_info)
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
