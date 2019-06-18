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
from lsst.ctrl.iip.ThreadManager import ThreadManager
from lsst.ctrl.iip.base import base

LOGGER = logging.getLogger(__name__)


class iip_base(base):
    """IIP Base class"""

    def __init__(self, filename, log_filename):
        super().__init__(filename, log_filename)
        self.thread_manager = self.setup_thread_manager()

    def setup_thread_manager(self):
        self.shutdown_event = threading.Event()
        self.shutdown_event.clear()
        thread_manager = ThreadManager('thread-manager', self.shutdown_event)
        thread_manager.start()
        return thread_manager

    def add_thread_groups(self, kws):
        self.thread_manager.add_thread_groups(kws)

    def setup_unpaired_publisher(self, url, name):
        self.thread_manager.add_unpaired_publisher_thread(url, name)

    def publish_message(self, route_key, msg):
        # we have to get the publisher each time because we can't guarantee that the publisher
        # that was first created hasn't died and been replaced
        consumer_name = threading.currentThread().getName()

        pub = self.thread_manager.get_publisher_paired_with(consumer_name)
        pub.publish_message(route_key, msg)
