import random
from SimplePublisher import * 
from Consumer import * 

class RegisterForeman: 
    """ We should probably have a parent class called RegisterFM
        and child classes called RegisterBaseForeman and RegisterNcsaForeman.
        All child classes do is change class level variables. Like Broker_username = "Base_FM"
        
        TODO: 
        1. generate_random has to handle more than [1, 10)
           a. worst case: random cannot find the remaining number and it loops for a while
        2. be able to handle both forwarder and distributor
        3. when i dump the message, i should use xml to validate those.(should)
        4. if the machine sends again, we would like to be able to record as different machine
           a. we can purge queues after each session
        5. change consumer to topic exchange
    """ 
    BROKER_USRNAME = "NCSA_FM"
    BROKER_PASSWD = "NCSA_FM"
    BROKER_ADDR = "141.142.208.241/%2fregi"
    CONSUME_QUEUE = "registering_machine"
    PUBLISH_QUEUE = "responding_ack"
    MACHINES = {}

    def __init__(self): 
        self._broker_username = self.BROKER_USRNAME
        self._broker_password = self.BROKER_PASSWD
        self._broker_addr = self.BROKER_ADDR
        self._amqpurl = "amqp://" + self._broker_username + ":" + self._broker_password + "@" + self._broker_addr
        self.setup_publisher()
        self.setup_consumer()
        self._machines = {} 

    def setup_publisher(self): 
        # "yaml" is default place holder, can't put in anything and this looks dumb
        self._publisher = SimplePublisher(self._amqpurl, "yaml")  

    def setup_consumer(self): 
        self._consumer = Consumer(self._amqpurl, self.CONSUME_QUEUE)
        
    def callback_consumer(self, ch, method, properties, body): 
        print("[x] Message Received %r " % body)
        self.publisher_info(yaml.load(body))

    def consumer_info(self): 
        self._consumer.run(self.callback_consumer)

    def publisher_info(self, machine_info): 
        # request next fqn
        sequence_number = self.generate_random()
        account = "F_" + str(sequence_number)
        SN = {}
        SN["FQN"] = self._machines[sequence_number]
        SN["CONSUME_QUEUE"] = "F" + str(sequence_number) + "_consume"
        SN["PUBLISH_QUEUE"] = "forwarder_publish"
        SN["IP_ADDR"] = machine_info["IP_ADDR"]
        SN["USRNAME"] = account 
        SN["PASSWD"] = account
        print("[x] Sent message is %r", yaml.dump(SN))
        self._publisher.publish_message(self.PUBLISH_QUEUE, yaml.dump(SN))

    def generate_random(self): 
        number = 1
        while number not in self._machines.keys(): 
            number = random.randrange(number, number+10)
            self._machines[number] = "FORWARDER_" + str(number)
        return number

    def run(self): 
        self.consumer_info()

def main(): 
    rForeman = RegisterForeman()
    rForeman.run() 

if __name__ == "__main__": 
    main()         
        
