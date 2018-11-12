import sys
sys.path.append("../")
from SimplePublisher import SimplePublisher
from Consumer import Consumer
import toolsmod
from time import sleep
import logging
import copy

class Premium:
    def __init__(self):
        logging.basicConfig()
        broker_url = "amqp://ARCHIE:ARCHIE@140.252.32.128:5672/%2Ftest_at"

        self.new_thread = Consumer(broker_url, 'telemetry_queue', 'xthread', self.mycallback, 'YAML')
        self.new_thread.start()

        self.publisher = SimplePublisher('amqp://DMCS:DMCS@140.252.32.128:5672/%2Ftest_at', "YAML")

        self.send_messages()
        sleep(5)

        self.new_thread.stop()

    def mycallback(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        msg = copy.deepcopy(body)
        if msg["STATUS_CODE"] == 1: 
            print("Result is: PASSED")
            exit
        else: 
            print("Result is: FAILED")

    def send_messages(self): 

        IMAGE_ID = "bunny"

        msg = {}
        msg['MSG_TYPE'] = "DMCS_AT_START_INTEGRATION"
        msg['IMAGE_ID'] = IMAGE_ID
        msg['IMAGE_INDEX'] = '2'
        msg['IMAGE_SEQUENCE_NAME'] = 'MAIN'
        msg['IMAGES_IN_SEQUENCE'] = '3'
        msg['ACK_ID'] = 'START_INT_ACK_76'
        msg['REPLY_QUEUE'] = "dmcs_ack_consume"
        self.publisher.publish_message("ocs_dmcs_consume", msg)
        print("START_INTEGRATION Message")
        sleep(5)

        msg = {}
        msg['MSG_TYPE'] = "DMCS_AT_END_READOUT"
        msg['IMAGE_ID'] = IMAGE_ID
        msg['IMAGE_INDEX'] = '2'
        msg['IMAGE_SEQUENCE_NAME'] = 'MAIN'
        msg['IMAGES_IN_SEQUENCE'] = '3'
        msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
        msg['ACK_ID'] = 'READOUT_ACK_77'
        self.publisher.publish_message("ocs_dmcs_consume", msg)
        print("READOUT Message")
        sleep(5)

        msg = {}
        msg["MSG_TYPE"] = "DMCS_AT_HEADER_READY"
        msg["IMAGE_ID"] = IMAGE_ID 
        msg["FILENAME"] = "http://localhost:8000/visitJune-28.header"
        self.publisher.publish_message("ocs_dmcs_consume", msg)
        print("HEADER_READY Message")
        sleep(5)

        print("Sender done")

def main():
    p = Premium()

if __name__ == "__main__":  main()
