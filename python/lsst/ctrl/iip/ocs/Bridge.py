# This file is part of ctrl_iip
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import time
from lsst.ctrl.iip.iip_base import iip_base
from lsst.ctrl.iip.AsyncPublisher import AsyncPublisher
from lsst.ctrl.iip.Consumer import Consumer
from lsst.ctrl.iip.ocs.Responder import Responder
from lsst.ctrl.iip.ocs.TelemetryForwarder import TelemetryForwarder

LOGGER = logging.getLogger(__name__)


class Bridge(iip_base):
    """Represents a base level communication conduit for messages from
    SAL to RabbitMQ

    Parameters
    ----------
    config_filename: `str`
        configuration file name to load
    log_filename: `str`
        file to write log messages to
    """

    def __init__(self, config_filename, log_filename):
        super().__init__(config_filename, log_filename)

        self.actions = []

        cred = self.getCredentials()
        self.service_user = cred.getUser('service_user')
        self.service_passwd = cred.getUser('service_passwd')

        config = self.getConfiguration()
        self.publishq = config['ROOT']['OCS']['OCS_PUBLISH']
        self.consumeq = config['ROOT']['OCS']['OCS_CONSUME']
        broker = config['ROOT']['BASE_BROKER_ADDR']

        url = 'amqp://%s:%s@%s' % (self.service_user, self.service_passwd, broker)
        self.bookkeeping_publisher = AsyncPublisher(url, 'bookkeeping')

        self.ack_publisher = AsyncPublisher(url, 'ack_publisher')

        self.devices = None

        self.ERROR_CODE_PREFIX = 5600

        self.responder = Responder(self)

        # setup rabbitmq consumer to listen to DMCS
        self.consumer = Consumer(url, self.consumeq, "Thread-dmcs_ocs_publish",
                                 self.responder.on_dmcs_message, "YAML")

        self.telemetry_forwarder = TelemetryForwarder(self, url)

    def register_devices(self, devices):
        """Register devices with this bridge. Note that setting
        "sendLocalAcks" to True means that the acknowledgements are sent back
        from the OCS Bridge, not from the outside devices.  This is done for
        standalone testing.
        @param devices: list of DeviceProxy objects to register
        @param sendLocalAcks: flag to tell the bridge to acknowledge locally
        """
        self.devices = devices
        for device in self.devices:
            device.register_message_sender(self.ack_publisher, self.publishq)
            device.register_message_bookkeeper(self.bookkeeping_publisher, self.consumeq)
            device.setup_processors()
            device.setup_log_events()
            device.setup_events()
            device.create_actions()

    def get_device(self, abbr):
        """Retreive the device given it's abbreviation
        @param abbr: abbreviation of the device name
        @return the full device name
        """
        for device in self.devices:
            if device.get_abbreviation() == abbr:
                return device
        return None

    def listen_loop(self):
        """Continous loop which cycles through all the registered devices
        attempting to retrieve messages each device is capable of retrieving.
        This method returns when self.shut_down_event is set.
        """

        # start RabbitMQ async listeners
        self.bookkeeping_publisher.start()
        self.ack_publisher.start()
        self.consumer.start()
        self.telemetry_forwarder.start()

        LOGGER.info("listening")
        print("listening")
        while True:
            for device in self.devices:
                device.accept_cmds()
                device.accept_events()
            if self.shutdown_event.is_set():
                return
            time.sleep(0.1)  # eech

    def shutdown(self):
        """Shutdown method to stop the non-SAL message threads and then exit.
        This is usually invoked by the signal handler code.
        """
        print("shutting down threads...")
        self.bookkeeping_publisher.stop()
        self.ack_publisher.stop()
        self.telemetry_forwarder.stop()
        self.consumer.stop()
        self.shutdown_event.set()
        self.thread_manager.shutdown_threads()
        print("done")
