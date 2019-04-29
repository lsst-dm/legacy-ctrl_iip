import time
from lsst.ctrl.iip.SimplePublisher import SimplePublisher

if __name__ == "__main__":
    sp1 = SimplePublisher('amqp://DMCS:DMCS@141.142.238.10:5672/%2Ftest_at', "YAML")

    msg = {}
    msg['MSG_TYPE'] = "RESET_FROM_FAULT"
    msg['DEVICE'] = 'AT'
    msg['ACK_ID'] = 'AT_13'
    msg['CMD_ID'] = '4434278818'
    time.sleep(3)
    print("AT RESET_FROM_FAULT")
    sp1.publish_message("ocs_dmcs_consume", msg)

    sp1.close()
