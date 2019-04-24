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


import pika
from pika.exceptions import AMQPError
import logging
import sys
from lsst.ctrl.iip.XMLHandler import XMLHandler
from lsst.ctrl.iip.YamlHandler import YamlHandler

LOGGER = logging.getLogger(__name__)


class SimplePublisher:

    EXCHANGE = 'message'

    def __init__(self, amqp_url, formatOptions=None):

        self._connection = None
        self._channel = None
        self._message_number = 0
        self._stopping = False
        self._url = amqp_url
        self._closing = False
        self._xml_handler = None
        self._format_options = formatOptions

        if formatOptions == "XML":
            self._message_handler = XMLHandler()
        else:
            self._message_handler = YamlHandler()

        try:
            self.connect()
        except Exception:
            LOGGER.error('No channel - connection channel is None')

    def connect(self):
        self._connection = pika.BlockingConnection(pika.URLParameters(self._url))
        self._channel = self._connection.channel()
        if self._channel is None:
            LOGGER.error('No channel - connection channel is None')

    def publish(self, route_key, msg):
        try:
            self._channel.basic_publish(exchange=self.EXCHANGE, routing_key=route_key, body=msg)
        except pika.exceptions.ConnectionClosed:
            LOGGER.critical("Connection timed out. Reconnected and republish message")
            self.connect()
            self.publish(route_key, msg)

    def close(self):
        self._channel.close()
        self._connection.close()
        self._connection = None
        self._channel = None

    def publish_message(self, route_key, msg):

        encoded_data = None

        # YAML
        encoded_data = self._message_handler.encode_message(msg)

        LOGGER.debug("Sending msg to %s", route_key)

        if self._channel is None or self._channel.is_closed is True:
            try:
                self.connect()
            except AMQPError:
                LOGGER.critical('Unable to create connection to rabbit server. Heading for exit...')
                sys.exit(105)

        self.publish(route_key, encoded_data)
