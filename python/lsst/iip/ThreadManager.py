###############################################################################
###############################################################################
## Copyright 2000-2018 The Board of Trustees of the University of Illinois.
## All rights reserved.
##
## Developed by:
##
##   LSST Image Ingest and Distribution Team
##   National Center for Supercomputing Applications
##   University of Illinois
##   http://www.ncsa.illinois.edu/enabling/data/lsst
##
## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal with the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:
##
##   Redistributions of source code must retain the above copyright
##   notice, this list of conditions and the following disclaimers.
##
##   Redistributions in binary form must reproduce the above copyright
##   notice, this list of conditions and the following disclaimers in the
##   documentation and/or other materials provided with the distribution.
##
##   Neither the names of the National Center for Supercomputing
##   Applications, the University of Illinois, nor the names of its
##   contributors may be used to endorse or promote products derived from
##   this Software without specific prior written permission.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
## IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR
## ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
## CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
## WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE SOFTWARE.



import threading
import logging
from time import sleep
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from copy import deepcopy

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
#logging.basicConfig(filename='logs/ThreadManager.log', level=logging.DEBUG, format=LOG_FORMAT)



class ThreadManager(threading.Thread):
    def __init__(self, name, kwargs, shutdown_event):
        threading.Thread.__init__(self, group=None, target=None, name=name) 
        self.running_threads = []
        self.shutdown_event = shutdown_event

        #self.consumer_kwargs = deepcopy(kwargs)
        self.consumer_kwargs = kwargs

        consumers = list(self.consumer_kwargs.keys())
        for consumer in consumers:
            x = self.setup_consumer_thread(self.consumer_kwargs[consumer])
            self.running_threads.append(x)

    def run(self):
        self.start_background_loop()

    def setup_consumer_thread(self, consumer_params):
        url = consumer_params['amqp_url']
        q = consumer_params['queue']
        threadname = consumer_params['name']
        callback = consumer_params['callback']
        format = consumer_params['format']

        new_thread = Consumer(url, q, threadname, callback, format)
        new_thread.start()
        sleep(1)
        return new_thread


    def start_background_loop(self):
        # Time for threads to start and quiesce
        sleep(2)
        try:
            while 1:
                # self.get_next_backlog_item() 
                if self.shutdown_event.isSet():
                    self.shutdown_consumers()
                    break
                sleep(1)
                self.check_thread_health()
                # self.resolve_non-blocking_acks() 
        except KeyboardInterrupt:
            pass


    def check_thread_health(self):
        num_threads = len(self.running_threads)
        for i in range(0, num_threads):
            if self.running_threads[i].is_alive():
                continue
            else:
                LOGGER.critical("Thread with name %s has died. Attempting to restart..." 
                                 % self.running_threads[i].name)
                dead_thread_name = self.running_threads[i].name
                del self.running_threads[i]
                ### Restart thread...
                new_consumer = self.setup_consumer_thread(self.consumer_kwargs[dead_thread_name])

                self.running_threads.append(new_consumer)


    def shutdown_consumers(self):
        num_threads = len(self.running_threads)
        for i in range (0, num_threads):
            LOGGER.info("Stopping rabbit connection in consumer %s" % self.running_threads[i].name)
            self.running_threads[i].stop()
            LOGGER.info("Shutting down consumer %s" % self.running_threads[i].name)
            self.running_threads[i].join()
            sleep(0.5)


