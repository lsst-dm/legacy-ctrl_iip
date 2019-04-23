import toolsmod
from Consumer import Consumer
from SimplePublisher import SimplePublisher
import logging
import _thread


class Premium:
    def __init__(self):
        logging.basicConfig()
        self.ack_test = True
        broker_url = 'amqp://BASE:BASE@141.142.208.191:5672/%2Fbunny'
        self.sp1 = SimplePublisher('amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny')

        cdm = toolsmod.intake_yaml_file('ForemanCfg.yaml')
        self.fdict = cdm['ROOT']['XFER_COMPONENTS']['ARCHIVE_FORWARDERS']
        self.fwdrs = list(self.fdict.keys())

        self._cons = Consumer(broker_url, 'dmcs_ack_consume', "YAML")
        try:
            _thread.start_new_thread(self.do_it, ("thread-1", 2,))
        except Exception as e:
            print("Cannot start thread")
            print(e)

    def mycallback(self, ch, methon, properties, body):
        print("  ")
        print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<")
        print((" [x] method Received %r" % methon))
        print((" [y] properties Received %r" % properties))
        print((" [z] body Received %r" % body))

        if self.ack_test:
            # grab name of fwdr from list, and ack respond as it...
            pass

        print("Message done")
        print("Still listening...")

    def do_it(self, threadname, delay):
        # example = ExampleConsumer('amqp://Fm:Fm@141.142.208.191:5672/%2Fbunny')
        print("Before run call")
        self._cons.run(self.mycallback)
        print("After run call - not blocking")


if __name__ == "__main__":
    premium = Premium()
    while 1:
        pass
