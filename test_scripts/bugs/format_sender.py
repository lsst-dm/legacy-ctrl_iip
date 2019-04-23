# This code does not work.  It expects to have a method named "FORMAT_DATA" that returns a filename,
# but it doesn't exist.
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from copy import deepcopy
import time
import logging


class Premium:
    def __init__(self):
        logging.basicConfig()
        broker_url = 'amqp://PFM:PFM@141.142.238.10:5672/%2Fbunny'
        self._cons = Consumer(broker_url, 'fetch_consume_from_f1', "Threadthread", self.mycallback, "YAML")
        self.Readout_Image_IDs = []
        self.Header_Info_Dict = {}
        self.Take_Images_Done_Message = {}

    def mycallback(self, ch, methon, properties, body):
        print("  ")
        print(">>>>>>>>>>>>>>>NEW MESSAGE<<<<<<<<<<<<<<<<")
        print((" [z] body Received %r" % body))

        msg_type = body['MSG_TYPE']
        if msg_type == "FORMAT_END_READOUT":
            self.Readout_Image_IDs.append(body['IMAGE_ID'])
            self.look_for_work()
        elif msg_type == "HEADER_FILE":
            filename = body['FILE_NAME']
            img_id = body['IMAGE_ID']
            self.Header_Info_Dict[img_id] = filename
            self.look_for_work()
        elif msg_type == "FORMAT_TAKE_IMAGES_DONE":
            self.Take_Images_Done_Message = deepcopy(body)
            self.look_for_work()

        print("Message done")
        print("Still listening...")

    def look_for_work(self):
        if self.Readout_Image_IDs is not None:
            for i in range(0, len(self.Readout_Image_IDs)):
                id = self.Readout_Image_IDs[i]
                if self.Header_Info_Dict.exists(id):
                    msg = {}
                    self.Readout_Image_IDs.pop(i)
                    header_filename = self.Header_Info_Dict[id]
                    self.Header_Info_Dict.pop(id, 0)
                    # formatted_filename = self.FORMAT_DATA(header_filename, id)
                    msg['MSG_TYPE'] = "FORWARD_END_READOUT"
                    msg['FILE_NAME'] = formatted_filename
                    msg['IMAGE_ID'] = id
        if (self.Readout_Image_IDs is None) and (self.Take_Images_Done_Message is None):
            return
        if (self.Readout_Image_IDs is None) and (self.Take_Images_Done_Message is not None):
            message = {}
            message = self.Take_Images_Done_Message
            message['MSG_TYPE'] = "FORWARD_TAKE_IMAGES_DONE"
            print("Outgoing FORWARD_TAKE_IMAGES_DONE message is: ")
            print(message)
            # publish message


if __name__ == "__main__":
    premium = Premium()
    sp1 = SimplePublisher('amqp://PFM:PFM@141.142.238.10:5672/%2Fbunny', "YAML")

    time.sleep(3)
    msg = {}
    msg['MSG_TYPE'] = "FORMAT_END_READOUT"
    msg['IMAGE_ID'] = "Img_X14001"
    time.sleep(2)
    sp1.publish_message("format_consume_from_f1", msg)

    msg = {}
    msg['MSG_TYPE'] = "FORMAT_END_READOUT"
    msg['IMAGE_ID'] = 'Img_X14022'
    time.sleep(4)
    sp1.publish_message("format_consume_from_f1", msg)

    msg = {}
    msg['MSG_TYPE'] = "HEADER_FILE"
    msg['FILE_NAME'] = 'X14001.fits'
    msg['IMAGE_ID'] = "Img_X14001"
    time.sleep(4)
    sp1.publish_message("format_consume_from_f1", msg)

    msg = {}
    msg['MSG_TYPE'] = "FORMAT_END_READOUT"
    msg['IMAGE_ID'] = "Img_X14028"
    time.sleep(2)
    sp1.publish_message("format_consume_from_f1", msg)

    msg = {}
    msg['MSG_TYPE'] = "FORMAT_TAKE_IMAGES_DONE"
    msg['IMAGE_ID'] = "Img_X14028"
    msg['ACK_ID'] = "ack_14"
    msg['REPLY_QUEUE'] = "ocs_dmcs_consume"
    time.sleep(1)
    sp1.publish_message("format_consume_from_f1", msg)

    msg['MSG_TYPE'] = "HEADER_FILE"
    msg['FILE_NAME'] = 'X14022.fits'
    msg['IMAGE_ID'] = "Img_X14022"
    time.sleep(4)
    sp1.publish_message("format_consume_from_f1", msg)

    msg['MSG_TYPE'] = "HEADER_FILE"
    msg['FILE_NAME'] = 'X14028.fits'
    msg['IMAGE_ID'] = "Img_X14028"
    time.sleep(4)
    sp1.publish_message("format_consume_from_f1", msg)

    print("Sender done")
