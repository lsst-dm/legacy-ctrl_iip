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
from lsst.ctrl.iip.toolsmod import L1Error

LOGGER = logging.getLogger(__name__)


class Responder:
    """Responds via SAL to messages received by the bridge
    """

    def __init__(self, bridge):
        self.bridge = bridge

    def on_dmcs_message(self, ch, method, properties, msg_dict):
        """ Calls the appropriate OCS action handler according to message type.
            @params ch: Channel to message broker, unused unless testing.
            @params method: Delivery method from Pika, unused unless testing.
            @params properties: Properties from OCSBridge callback message body.
            @params msg_dict: A dictionary that stores the message body.
            @return: None
        """
        ch.basic_ack(method.delivery_tag)
        LOGGER.info("Processing message in DMCS message callback")
        LOGGER.info("Message and properties from DMCS callback message body is: %s and %s" %
                    (str(msg_dict), properties))

        try:
            device_abbr = msg_dict["DEVICE"]
            device = self.bridge.get_device(device_abbr)
            if device is None:
                LOGGER.error("%s is not in registered devices" % device_abbr)
                return
            device.outgoing_message_handler(msg_dict)
        except KeyError as e:
            msg = "Bridge received malformed  message: %s" % e.args
            LOGGER.error(msg)
        except Exception as e:
            msg = "Bridge unable to act on on_dmcs_message: %s" % e.args
            LOGGER.error(msg)

    def process_book_keeping(self, msg_dict):
        pass

    def process_resolve_ack(self, msg_dict):
        pass
