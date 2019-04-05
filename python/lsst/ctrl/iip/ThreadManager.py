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
from copy import deepcopy

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
        self.shutdown_event = shutdown_event
        self.lock = threading.Lock()


    #TODO: this method will go away once # we switch 
    # how consumer/publishers are handled in a future ticket
    def add_thread_groups(self, kwargs):
        names = list(kwargs.keys())
        print("names = ")
        print(names)
        for name in names:
            LOGGER.info("setting up threads for group %s" % name)
            print("setting up threads for group %s" % name)
            self.add_thread_group(kwargs[name])

    def add_thread_group(self, params):
        self.lock.acquire()

        thread_name = params['name']
        thread_info = self.ThreadInfo(thread_name, "consumer", params)
        self.registered_threads_info[thread_name] = thread_info

        (name, consumer_thread) = self.setup_consumer_thread(thread_info)
        self.running_threads[name] = consumer_thread

        # using this defensive in transition for code that hasn't been
        # ported to create consumers/publishers together
        if 'publisher_name' in params:
            thread_name = params['publisher_name']
            thread_info = self.ThreadInfo(thread_name, "publisher", params)
            (name, publisher_thread) = self.setup_publisher_thread(thread_info)
            self.running_threads[name] = publisher_thread
        else:
            print('---->')
            print("publisher_name not found")
            print(params)
            print('<-----')

        self.lock.release()

    def setup_consumer_thread(self, thread_info):
        consumer_params = thread_info.params

        url = consumer_params['amqp_url']
        q = consumer_params['queue']
        thread_name = consumer_params['name']
        callback = consumer_params['callback']
        dataformat = consumer_params['format']

        new_thread = Consumer(url, q, thread_name, callback, dataformat)
        new_thread.start()
        sleep(1) # XXX
        return (thread_name, new_thread)

    def setup_publisher_thread(self, thread_info):
        params = thread_info.params
        url = params['publisher_url']
        thread_name = params['publisher_name']
        LOGGER.info('starting AsyncPublisher %s' % thread_name)
        new_thread = AsyncPublisher(url, thread_name)
        new_thread.start()
        return (thread_name, new_thread)

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
                ### Restart thread...
                if self.shutdown_event.isSet() is False:
                        LOGGER.critical("Thread with name %s has died. Attempting to restart..." % dead_thread_name)
                        thread_info = self.registered_threads_info[dead_thread_name]
                        (new_name, new_consumer) = self.setup_consumer_thread(thread_info)
                        self.running_threads[new_name] = new_consumer
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

    def shutdown_threads2(self):
        self.lock.acquire()
        num_threads = len(self.running_threads)
        LOGGER.info("shutting down %d threads" % num_threads)
        for i in range (0, num_threads):
            LOGGER.info("Stopping rabbit connection in %s" % self.running_threads[i].name)
            self.running_threads[i].stop()
            LOGGER.info("Shutting down consumer %s" % self.running_threads[i].name)
            self.running_threads[i].join()
            LOGGER.info("consumer %s finished" % self.running_threads[i].name)
        self.lock.release()

        LOGGER.info("consumer thread shutdown completed")

    def run(self):
        self.start_background_loop()

