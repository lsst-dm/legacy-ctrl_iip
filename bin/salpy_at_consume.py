from lsst.ctrl.iip.iip_base import iip_base
from lsst.ctrl.iip.AsyncPublisher import AsyncPublisher
from lsst.ctrl.iip.Consumer import Consumer
import sys
import time
from SALPY_ATArchiver import *
import threading

import logging

class DMCS_Simulator(iip_base):
    def __init__(self, configfile):
        super().__init__(configfile, "DMCS_Simulator.log")

        cred = self.getCredentials()
        user = cred.getUser("service_user")
        passwd = cred.getPasswd("service_passwd")
        config = self.getConfiguration()
        broker_addr = config["ROOT"]["BASE_BROKER_ADDR"]
        url = "amqp://%s:%s@%s" % (user, passwd, broker_addr)

        self.asyncpub = AsyncPublisher(url, "pub")
        self.asyncpub.start()

        self.consumer = Consumer(url, "ocs_dmcs_consume", "thread-dmcs_simulator", self.on_message, "YAML")
        self.consumer.start()

    def on_message(self, ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        msg = {}
        msg["MSG_TYPE"] = body["MSG_TYPE"] + "_ACK"
        msg["CMD_ID"] = body["CMD_ID"]
        msg["DEVICE"] = body["DEVICE"]
        msg["ACK_ID"] = body["ACK_ID"]
        msg["ACK_BOOL"] = True
        msg["ACK_STATEMENT"] = "something good"
        print(msg)
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)

    def publish(self):
        msg = {}
        msg["MSG_TYPE"] = "summaryState"
        msg["DEVICE"] = "AT"
        msg["CURRENT_STATE"] = "DISABLE"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("SUMMARY STATE DISABLE")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "summaryState"
        msg["DEVICE"] = "AT"
        msg["CURRENT_STATE"] = "ENABLE"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("SUMMARY STATE ENABLE")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "summaryState"
        msg["DEVICE"] = "AT"
        msg["CURRENT_STATE"] = "FAULT"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("SUMMARY STATE FAULT")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "summaryState"
        msg["DEVICE"] = "AT"
        msg["CURRENT_STATE"] = "OFFLINE"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("SUMMARY STATE OFFLINE")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "summaryState"
        msg["DEVICE"] = "AT"
        msg["CURRENT_STATE"] = "STANDBY"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("SUMMARY STATE STANDBY")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "settingVersions"
        msg["DEVICE"] = "AT"
        msg["CFG_KEY"] = "Normal"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("SETTING VERSIONS")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "errorCode"
        msg["DEVICE"] = "AT"
        msg["ERROR_CODE"] = 56000
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("ERROR CODE")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "appliedSettingsMatchStart"
        msg["DEVICE"] = "AT"
        msg["APPLIED"] = True
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("APPLIED SETTINGS MATCH START")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "settingsApplied"
        msg["DEVICE"] = "AT"
        msg["TS_SAL_VERSION"] = "V3.9.0"
        msg["TS_XML_VERSION"] = "v3.9"
        msg["L1_DM_REPO_TAG"] = "Release 2.1"
        msg["SETTINGS"] = "Some settings"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("SETTINGS APPLIED")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "processingStatus"
        msg["DEVICE"] = "AT"
        msg["STATUS_CODE"] = 100
        msg["DESCRIPTION"] = "everything went fine"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("PROCESSING STATUS")
        time.sleep(1)

        """ Bad messages
        """
        msg = {}
        msg["MSG_TYPE"] = "summaryState"
        msg["DEVICE"] = "AT"
        msg["CURRENT_STATE"] = "BAD_STATE"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("BAD SUMMARY STATE STATE")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "settingVersions"
        msg["DEVICE"] = "AT"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("BAD SETTING VERSIONS")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "errorCode"
        msg["DEVICE"] = "AT"
        msg["ERROR_CODE"] = "HELLO"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("BAD ERROR CODE")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "appliedSettingsMatchStart"
        msg["DEVICE"] = "AT"
        msg["APPLIED"] = 100
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("BAD APPLIED SETTINGS MATCH START")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "settingsApplied"
        msg["DEVICE"] = "AT"
        msg["TS_XML_VERSION"] = "v3.9"
        msg["L1_DM_REPO_TAG"] = "Release 2.1"
        msg["SETTINGS"] = "Some settings"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("BAD SETTINGS APPLIED")
        time.sleep(1)

        msg = {}
        msg["MSG_TYPE"] = "processingStatus"
        msg["STATUS_CODE"] = 100
        msg["DESCRIPTION"] = "everything went fine"
        self.asyncpub.publish_message("dmcs_ocs_publish", msg)
        print("BAD PROCESSING STATUS")
        time.sleep(1)

    def halt(self):
        self.asyncpub.stop()
        self.consumer.stop()
        self.shutdown()  # shutdown the thread manager

if __name__ == "__main__":
    dmcs = DMCS_Simulator("L1SystemCfg.yaml")
    dmcs.publish()
    dmcs.halt()
    sys.exit(0)

