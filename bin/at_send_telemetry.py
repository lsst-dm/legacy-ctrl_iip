from lsst.ctrl.iip.iip_base import iip_base
from lsst.ctrl.iip.AsyncPublisher import AsyncPublisher
import sys
import time


class TelemetryEmitter(iip_base):
    def __init__(self, configfile):
        super().__init__(configfile, "TelemetryEmitter.log")

        cred = self.getCredentials()
        user = cred.getUser("service_user")
        passwd = cred.getPasswd("service_passwd")

        config = self.getConfiguration()

        broker_addr = config["ROOT"]["BASE_BROKER_ADDR"]
        url = f"amqp://{user}:{passwd}@{broker_addr}"

        self.asyncpub = AsyncPublisher(url, "pub")
        self.asyncpub.start()

    def publish(self):
        msg = {}
        msg["MSG_TYPE"] = "TELEMETRY"
        msg["DEVICE"] = "AT"
        msg["STATUS_CODE"] = 451
        msg["DESCRIPTION"] = "THIS IS A TELEMETRY TEST MESSAGE"
        self.asyncpub.publish_message("telemetry_queue", msg)
        print("TELEMETRY SENT")

    def halt(self):
        self.asyncpub.stop()
        self.shutdown()  # shutdown the thread manager


if __name__ == "__main__":
    dmcs = TelemetryEmitter("L1SystemCfg.yaml")
    dmcs.publish()
    time.sleep(5)
    dmcs.halt()
    sys.exit(0)
