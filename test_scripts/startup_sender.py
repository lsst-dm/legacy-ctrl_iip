from lsst.ctrl.iip.Consumer import Consumer
from lsst.ctrl.iip.SimplePublisher import SimplePublisher
import time
import logging
import _thread
import lsst.ctrl.iip.toolsmod as toolsmod


class Premium:
    def __init__(self):
        logging.basicConfig()
        broker_url = 'amqp://BASE:BASE@141.142.238.160:5672/%2Fbunny'

        self._cons = Consumer(broker_url, 'ar_foreman_consume', "YAML")
        try:
            _thread.start_new_thread(self.do_it, ("thread-1", 2,))
        except Exception as e:
            print("Cannot start thread")
            print(e)

        self._cons2 = Consumer(broker_url, 'pp_foreman_consume', "YAML")
        try:
            _thread.start_new_thread(self.do_it2, ("thread-3", 2,))
        except Exception as e:
            print("Cannot start thread")
            print(e)

        cdm = toolsmod.intake_yaml_file("L1SystemCfg.yaml")
        self.ccd_list = cdm['ROOT']['CCD_LIST']

    def mycallback(self, ch, methon, properties, body):
        print("  ")
        print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<")
        print((" [z] body Received %r" % body))
        print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<")

    def mycallback2(self, ch, methon, properties, body):
        print("  ")
        print("++++++++++++++-----------+++++++++++++++")
        print((" [z] body Received %r" % body))
        print("++++++++++++++-----------+++++++++++++++")

    def do_it(self, threadname, delay):
        print("Before run call")
        self._cons.run(self.mycallback)
        print("After run call - not blocking")

    def do_it2(self, threadname, delay):
        print("Before run call")
        self._cons2.run(self.mycallback2)
        print("After run call - not blocking")


if __name__ == "__main__":
    premium = Premium()

    sp1 = SimplePublisher('amqp://BASE_PUB:BASE_PUB@141.142.238.160:5672/%2Fbunny', "YAML")

    msg = {}
    msg['MSG_TYPE'] = "STANDBY"
    msg['DEVICE'] = 'AR'
    msg['CFG_KEY'] = "2C16"
    msg['ACK_ID'] = 'AR_4'
    msg['ACK_DELAY'] = 2
    msg['CMD_ID'] = '4434278812'
    time.sleep(3)
    print("AR STANDBY")
    sp1.publish_message("ocs_dmcs_consume", msg)

    msg = {}
    msg['MSG_TYPE'] = "DISABLE"
    msg['DEVICE'] = 'AR'
    msg['ACK_ID'] = 'AR_6'
    msg['ACK_DELAY'] = 2
    msg['CMD_ID'] = '4434278814'
    time.sleep(3)
    print("AR DISABLE")
    sp1.publish_message("ocs_dmcs_consume", msg)

    msg = {}
    msg['MSG_TYPE'] = "ENABLE"
    msg['DEVICE'] = 'AR'
    msg['ACK_ID'] = 'AR_11'
    msg['ACK_DELAY'] = 2
    msg['CMD_ID'] = '4434278816'
    time.sleep(3)
    print("AR ENABLE")
    sp1.publish_message("ocs_dmcs_consume", msg)

    time.sleep(15)

    print("Sender done")
