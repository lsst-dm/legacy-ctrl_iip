import sys
sys.path.append("../")
from SimplePublisher import SimplePublisher
import toolsmod
from time import sleep

class Premium:
    self.image_ids = [] 
    self.received_images = [] 

    def __init__(self):
        logging.basicConfig()
        broker_url = "amqp://ARCHIE:ARCHIE@140.252.32.128:5672/%2Ftest_at"

        self.new_thread = Consumer(broker_url, 'telemetry_queue', 'xthread', self.mycallback, 'YAML')
        self.new_thread.start()

        self.publisher = SimplePublisher('amqp://DMCS:DMCS@140.252.32.128:5672/%2Ftest_at', "YAML")

        # timer must be more
        self.send_messages()
        sleep(120)
        
        # check every success messages
        readout_set = set(self.received_images)
        assert(len(readout_set) == 1, "One of the images completed was successful.")
        assert(len(self.received_images) == len(self.image_ids), "Not every images were completed.")

    def mycallback(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        msg = yaml.load(body) 
        self.received_images.append(msg["STATUS_CODE"])

    def send_messages(): 
        for img_id in self.image_ids:
            msg = {}
            msg['MSG_TYPE'] = "DMCS_AT_START_INTEGRATION"
            msg['IMAGE_ID'] = img_id
            msg['IMAGE_INDEX'] = '2'
            msg['IMAGE_SEQUENCE_NAME'] = 'MAIN'
            msg['IMAGES_IN_SEQUENCE'] = '3'
            msg['ACK_ID'] = 'START_INT_ACK_76'
            msg['REPLY_QUEUE'] = "dmcs_ack_consume"
            self.publisher.publish_message("ocs_dmcs_consume", msg)
            print("START_INTEGRATION Message")
            time.sleep(0.5)

            msg = {}
            msg['MSG_TYPE'] = "DMCS_AT_END_READOUT"
            msg['IMAGE_ID'] = img_id
            msg['IMAGE_INDEX'] = '2'
            msg['IMAGE_SEQUENCE_NAME'] = 'MAIN'
            msg['IMAGES_IN_SEQUENCE'] = '3'
            msg['RESPONSE_QUEUE'] = "dmcs_ack_consume"
            msg['ACK_ID'] = 'READOUT_ACK_77'
            self.publisher.publish_message("ocs_dmcs_consume", msg)
            print("READOUT Message")
            time.sleep(0.5)

            msg = {}
            msg["MSG_TYPE"] = "DMCS_AT_HEADER_READY"
            msg["IMAGE_ID"] = img_id 
            msg["FILENAME"] = "http://localhost:8000/visitJune-28.header"
            self.publisher.publish_message("ocs_dmcs_consume", msg)
            print("HEADER_READY Message")
            time.sleep(0.5)

            print("%s img_id is Done." % img_id)
        print("Sender done")

def main():
    p = Premium()

if __name__ == "__main__":  main()
