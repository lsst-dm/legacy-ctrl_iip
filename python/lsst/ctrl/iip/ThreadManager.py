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


import threading
import logging
from time import sleep
from lsst.ctrl.iip.Consumer import Consumer
from lsst.ctrl.iip.AsyncPublisher import AsyncPublisher

LOGGER = logging.getLogger(__name__)


class ThreadManager(threading.Thread):

    class ThreadInfo:
        def __init__(self, thread_name, thread_type, params):
            self.thread_name = thread_name
            self.thread_type = thread_type
            self.params = params

    def __init__(self, name, shutdown_event):
        threading.Thread.__init__(self, group=None, target=None, name=name)
        self.registered_threads_info = {}
        self.running_threads = {}
        self.paired_name = {}
        self.shutdown_event = shutdown_event
        self.lock = threading.Lock()

    def add_thread_groups(self, kwargs):
        names = list(kwargs.keys())
        for name in names:
            LOGGER.info("setting up threads for group %s" % name)
            self.add_thread_group(kwargs[name])

    def add_thread_group(self, params):
        self.lock.acquire()

        # using this defensive in transition for code that hasn't been
        # ported to create consumers/publishers together
        publisher_name = None
        if 'publisher_name' in params:
            publisher_name = params['publisher_name']
            thread_info = self.ThreadInfo(publisher_name, "publisher", params)
            self.registered_threads_info[publisher_name] = thread_info

            publisher_thread = self.create_publisher_thread(params)
            self.running_threads[publisher_name] = publisher_thread

        consumer_name = params['name']
        thread_info = self.ThreadInfo(consumer_name, "consumer", params)
        self.registered_threads_info[consumer_name] = thread_info

        consumer_thread = self.create_consumer_thread(params)
        self.running_threads[consumer_name] = consumer_thread

        self.paired_name[consumer_name] = publisher_name
        self.lock.release()

    def add_unpaired_publisher_thread(self, publisher_url, publisher_name):
        """Create a thread with no associated consumer thread
        """
        self.lock.acquire()

        params = {}
        params['publisher_url'] = publisher_url
        params['publisher_name'] = publisher_name

        thread_info = self.ThreadInfo(publisher_name, "publisher", params)
        self.registered_threads_info[publisher_name] = thread_info

        publisher_thread = self.create_publisher_thread(params)
        self.running_threads[publisher_name] = publisher_thread

        main_thread_name = threading.main_thread().getName()
        self.paired_name[main_thread_name] = publisher_name
        self.lock.release()

    def create_consumer_thread(self, params):

        url = params['amqp_url']
        q = params['queue']
        consumer_name = params['name']
        callback = params['callback']
        dataformat = params['format']

        LOGGER.info('starting Consumer %s' % consumer_name)
        new_thread = Consumer(url, q, consumer_name, callback, dataformat)
        new_thread.start()
        sleep(1)  # XXX
        return new_thread

    def create_publisher_thread(self, params):
        url = params['publisher_url']
        publisher_name = params['publisher_name']

        LOGGER.info('starting AsyncPublisher %s' % publisher_name)
        new_thread = AsyncPublisher(url, publisher_name)
        new_thread.start()
        return new_thread

    def get_publisher_paired_with(self, consumer_name):
        self.lock.acquire()
        publisher_name = self.paired_name[consumer_name]
        thr = self.running_threads[publisher_name]
        self.lock.release()
        return thr

    def get_thread_by_name(self, name):
        self.lock.aquire()
        thr = self.running_threads[name]
        self.lock.release()
        return thr

    def start_background_loop(self):
        # Time for threads to start and quiesce
        sleep(2)
        while 1:
            # self.get_next_backlog_item()
            if self.shutdown_event.isSet():
                return
            sleep(1)
            self.check_thread_health()
            # self.resolve_non-blocking_acks()

    def check_thread_health(self):
        self.lock.acquire()

        for (cur_name, cur_thread) in list(self.running_threads.items()):
            if cur_thread.is_alive():
                continue
            else:
                dead_thread_name = cur_thread.name
                del self.running_threads[cur_name]
                # Restart thread...
                if self.shutdown_event.isSet() is False:
                    LOGGER.critical("Thread with name %s has died. Restarting..." % dead_thread_name)
                    thread_info = self.registered_threads_info[dead_thread_name]
                    if thread_info.thread_type == "consumer":
                        new_consumer = self.create_consumer_thread(thread_info.params)
                        self.running_threads[dead_thread_name] = new_consumer
                    else:
                        new_publisher = self.create_publisher_thread(thread_info.params)
                        self.running_threads[dead_thread_name] = new_publisher
        self.lock.release()

    def shutdown_threads(self):
        self.lock.acquire()
        LOGGER.info("shutting down %d threads" % len(self.running_threads))
        for (cur_name, cur_thread) in list(self.running_threads.items()):
            LOGGER.info("Stopping rabbit connection in %s" % cur_name)
            cur_thread.stop()
            LOGGER.info("Shutting down consumer %s" % cur_name)
            cur_thread.join()
            LOGGER.info("consumer %s finished" % cur_name)
        self.lock.release()

        LOGGER.info("consumer thread shutdown completed")

    def run(self):
        self.start_background_loop()
