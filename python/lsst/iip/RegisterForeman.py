import random
import logging
from SimplePublisher import * 
from Consumer import * 

logging.basicConfig()
class RegisterForeman: 
    """ We should probably have a parent class called RegisterFM
        and child classes called RegisterBaseForeman and RegisterNcsaForeman.
        All child classes do is change class level variables. Like Broker_username = "Base_FM"
        
        TODO: 
        2. be able to handle both forwarder and distributor
        4. if the machine sends again, we would like to be able to record as different machine
           a. we can purge queues after each session
        5. change consumer to topic exchange
        8. I have multiple connections in one file, instead of channels.
    """ 
    BROKER_USRNAME = "NCSA_FM"
    BROKER_PASSWD = "NCSA_FM"
    BROKER_ADDR = "141.142.208.241/%2fregi"
    CONSUME_QUEUE = "registering_machine"
    PUBLISH_QUEUE = "responding_ack"
    EXCHANGE = "register_msg"
    MACHINES = [] 
    SEED = 1

    def __init__(self): 
        self._broker_username = self.BROKER_USRNAME
        self._broker_password = self.BROKER_PASSWD
        self._broker_addr = self.BROKER_ADDR
        self._amqpurl = "amqp://" + self._broker_username + ":" + self._broker_password + "@" + self._broker_addr
        self.setup_consumer()
        self.setup_publisher()
        self._machines = self.MACHINES 

    def setup_publisher(self): 
        self._publisher = SimplePublisher(self._amqpurl, exchange=self.EXCHANGE, formatOptions="yaml")  

    def setup_consumer(self): 
        self._consumer = Consumer(self._amqpurl, self.CONSUME_QUEUE)
        
    def callback_consumer(self, ch, method, properties, body): 
        print("[x] Message Received %r " % body)
        self._consumer.acknowledge_message(method.delivery_tag)
        self.publisher_info(yaml.load(body))

    def consumer_info(self): 
        self._consumer.run(self.callback_consumer)

    def publisher_info(self, machine_info): 
        # request next fqn
        sequence_number = self.generate_random()
        account = "F_" + str(sequence_number)
        SN = {}
        SN["FQN"] = "FORWARDER_" + str(sequence_number)
        SN["CONSUME_QUEUE"] = "F" + str(sequence_number) + "_consume"
        SN["PUBLISH_QUEUE"] = "forwarder_publish"
        SN["IP_ADDR"] = machine_info["IP_ADDR"]
        SN["USRNAME"] = account 
        SN["PASSWD"] = account
        print("[x] Sent message is %r"% yaml.dump(SN))
        self._publisher.publish_message(self.PUBLISH_QUEUE, yaml.dump(SN))
        print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

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
        self.consumer_info()

def main(): 
    rForeman = RegisterForeman()
    rForeman.run() 

if __name__ == "__main__": 
    main()         
        
