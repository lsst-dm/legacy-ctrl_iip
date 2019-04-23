from lsst.ctrl.iip.SimplePublisher import SimplePublisher
import time
import logging

if __name__ == "__main__":
    logging.basicConfig()
    sp1 = SimplePublisher('amqp://PFM:PFM@141.142.238.10:5672/%2Fbunny', "YAML")

    time.sleep(3)

    msg = {}
    msg['MSG_TYPE'] = "DO_SOMETHING"
    msg['RAFT_LIST'] = ['01', '11', '22', '31', '40']
    msg['RAFT_CCD_LIST'] = [['52', '54'], ['53', '60', '62'], ['ALL'], ['65', '68'], ['42', '11', '12', '14']]
    time.sleep(2)
    sp1.publish_message("ocs_dmcs_consume", msg)

    print("Sender done")
