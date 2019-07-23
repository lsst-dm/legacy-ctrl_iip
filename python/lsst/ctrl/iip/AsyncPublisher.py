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
import threading
import sys
import pika
from pprint import pformat
from pika.exceptions import AMQPError
from lsst.ctrl.iip.YamlHandler import YamlHandler

LOGGER = logging.getLogger(__name__)


class AsyncPublisher(threading.Thread):

    def __init__(self, amqp_url, name):
        threading.Thread.__init__(self, group=None, target=None, name=name)

        self.exchange = 'message'
        self.exchange_type = 'direct'
        self._connection = None
        self._channel = None
        self._url = amqp_url
        self.setup_complete_event = threading.Event()
        self.setup_complete_event.clear()

        self._message_handler = YamlHandler()


    def connect(self):
        self._connection = pika.SelectConnection(pika.URLParameters(self._url),
                                                 on_open_callback=self.on_connection_open,
                                                 on_close_callback=self.on_connection_closed)

    def on_connection_open(self, connection):
        LOGGER.info("connection opened")
        self._connection = connection
        self.open_channel()

    def open_channel(self):
        LOGGER.info("creating a new channel")
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        LOGGER.info("channel opened")
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_complete_event.set()

    def add_on_channel_close_callback(self):
        LOGGER.info('adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        LOGGER.info('Channel %i was closed %s' % (channel, reason))
        self._channel = None
        self._connection.close()

    def on_connection_closed(self, connection, reason):
        """
        Params:
            connection - closed object connection
            reason - reason for closure
        """
        self._channel = None
        self._connect = None

    def close(self):
        self._channel.close()
        self._connection.close()

    def publish_message(self, route_key, msg):

        encoded_data = self._message_handler.encode_message(msg)

        LOGGER.info("Sending msg to %s", route_key)

        # TODO:  This if-clause likely should be taken out.
        if self._channel is None or self._channel.is_closed is True:
            try:
                self.connect()
            except AMQPError:
                LOGGER.critical('Unable to create connection to rabbit server. Heading for exit...')
                sys.exit(105)  # XXX - why 105?

        # Since this is asynchronous, it's possible to still be in the
        # process of getting setup and having self._channel be None when
        # publish_message is being called from another thread, so we wait
        # here until setup is completed.
        if self.setup_complete_event.wait():
            self._channel.basic_publish(exchange='message', routing_key=route_key, body=encoded_data)
            LOGGER.info('message sent message body is: %s', pformat(str(msg)))

    def stop(self):
        LOGGER.info('Stopping')
        self._connection.ioloop.stop()
        LOGGER.info('Stopped')

    def run(self):
        try:
            self.connect()
        except Exception:
            LOGGER.error('No channel - connection channel is None')
        self._connection.ioloop.start()
