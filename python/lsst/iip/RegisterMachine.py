import logging
import subprocess
import yaml
from Consumer import *
from SimplePublisher import *
            
class RegisterMachine:
    """ FoodForThought: 
        1. We should have helper class like read_yaml, which is repeated everywhere
        2. GLOBAL VARIABLE should be moved to a single file
        3. guest useraccount cannot be used coz guest can connect only via localhost

        Running: 
        * RegisterForeman has to run first, so that consumer does declare_q, bind_q
        * Logging level is set to CRITICAL. There is warning for shutting down, but won't show up.

        Assumption: 
        * broker is at 141.142.208.241 and vhost regi is created beforehand
        * "hostname" command works // can use socket.gethostname() instead
        * "hostname -I" command works // a workaround maybe using socket package(python built-in)
        
        TODO: 
        1. 
    """ 
    CONSUME_QUEUE = "responding_ack"
    PUBLISH_QUEUE = "registering_machine"
    BROKER_ADDR = "141.142.208.241/%2fregi"
    BROKER_USRNAME = "REGI"
    BROKER_PASSWD = "REGI"

    def __init__(self): 
        self._broker_username = self.BROKER_USRNAME 
        self._broker_password = self.BROKER_PASSWD
        self._broker_addr = self.BROKER_ADDR 
        self._amqpurl = "amqp://" + self._broker_username + ":" + self._broker_password + "@" + self._broker_addr
        self._hostname = self.get_hostname()
        self._ip_addr = self.get_ip_addr()
        self.setup_publisher()
        self.setup_consumer() 
    
    def setup_publisher(self): 
        """ SimplePublisher might want to change to include exchange name
            so that we can use different exchange instead of message
            probably we should be fine since we are using different vhost
        """ 
        self._publisher = SimplePublisher(self._amqpurl, "yaml")

    def setup_consumer(self): 
        self._consumer = Consumer(self._amqpurl, self.CONSUME_QUEUE) 

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
        machine_info["HOSTNAME"] = self._hostname
        machine_info["IP_ADDR"] = self._ip_addr
        self._publisher.publish_message(self.PUBLISH_QUEUE, yaml.dump(machine_info))
        print("[x] Message Sent.")
    
    def consume_info(self): 
        self._consumer.run(self.callback_consumer)

    def callback_consumer(self, ch, method, properties, body): 
        SN = yaml.load(body)
        if (SN["IP_ADDR"] == self._ip_addr): 
            print("[x] Msg Received. %r" % body)
            self._consumer.stop()

    def register(self): 
        self.publish_info()
        self.consume_info()

def main(): 
    logging.basicConfig(level=logging.CRITICAL)
    machine = RegisterMachine()
    machine.register() 

if __name__ == "__main__": 
    main() 
