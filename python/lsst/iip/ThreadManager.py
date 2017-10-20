import threading
import logging
from time import sleep
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from copy import deepcopy

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename='logs/ThreadManager.log', level=logging.DEBUG, format=LOG_FORMAT)



class ThreadManager(threading.Thread):
    def __init__(self, name, kwargs):
        threading.Thread.__init__(self, group=None, target=None, name=name) 
        self.running_threads = []

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
        test_val = consumer_params['test_val']
#need to keep copies of the events
#so it cen set it.
        new_thread = Consumer(url, q, threadname, callback, format, test_val)
        new_thread.start()
        sleep(1)
        return new_thread


    def start_background_loop(self):
        # Time for threads to start and quiesce
        sleep(2)
        try:
            while 1:
#check if I need to shutdown then call a function that sets each event
#if they're all set then end myself.
                # self.get_next_backlog_item() ???
                sleep(1)
                self.check_thread_health()
                # self.resolve_non-blocking_acks() ???
        except KeyboardInterrupt:
            pass
#just use one event
#need to join at some point?
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

