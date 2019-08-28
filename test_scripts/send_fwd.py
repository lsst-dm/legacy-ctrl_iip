from lsst.ctrl.iip.SimplePublisher import SimplePublisher
from lsst.ctrl.iip.base import base
import time

def main():
    instance = base("L1SystemCfg.yaml", "fwd_sender.log")
    cred = instance.getCredentials()
    user = cred.getUser('service_user')
    passwd = cred.getPasswd('service_passwd')

    cfg = instance.getConfiguration()
    vhost = cfg["ROOT"]["BASE_BROKER_ADDR"]

    url = f'amqp://%s:%s@%s' % (user, passwd, vhost)
    sp = SimplePublisher(url, "YAML")

    image_id = "AT_O_20190730_000005"

    msg = {}
    msg["MSG_TYPE"] = "AT_FWDR_HEALTH_CHECK"
    msg["REPLY_QUEUE"] = "at_foreman_ack_publish"
    msg["ACK_ID"] = "ack_100"
    sp.publish_message("f99_consume", msg)
    time.sleep(1)

    msg = {}
    msg["MSG_TYPE"] = "AT_FWDR_XFER_PARAMS"
    msg["REPLY_QUEUE"] = "at_foreman_ack_publish"
    msg["IMAGE_ID"] = image_id
    msg["ACK_ID"] = "ack_100"
    msg["TARGET_LOCATION"] = "ARC@141.142.238.15:/data/export"
    msg["RAFT_LIST"] = ['00']
    msg["RAFT_CCD_LIST"] = ['00']
    sp.publish_message("f99_consume", msg)
    time.sleep(1)

    msg = {}
    msg["MSG_TYPE"] = "AT_FWDR_HEADER_READY"
    msg["REPLY_QUEUE"] = "at_foreman_ack_publish"
    msg["ACK_ID"] = "ack_100"
    msg["IMAGE_ID"] = image_id
    msg["FILENAME"] = "http://localhost:8000/ats.header"
    sp.publish_message("f99_consume", msg)
    time.sleep(1)

    msg = {}
    msg["MSG_TYPE"] = "AT_FWDR_END_READOUT"
    msg["REPLY_QUEUE"] = "at_foreman_ack_publish"
    msg["IMAGE_ID"] = image_id
    msg["ACK_ID"] = "ack_100"
    sp.publish_message("f99_consume", msg)
    time.sleep(1)

if __name__ == "__main__":
    main()
