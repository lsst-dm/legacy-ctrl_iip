from time import sleep
import os
import threading

class BaseMgmt:

    def __init__(self):
'''
<<<<<<< HEAD
=======
        pass
>>>>>>> 633362af6748ef31c2e0f9c4b7f088800c39bf36
'''
    self.shutdown_event = threading.Event()
    self.shutdown_event.clear()


    def ack_timer(self, seconds):
        sleep(seconds)
        return True

    def shutdown(self):
        self.shutdown_event.set()
        os.exit(0)
