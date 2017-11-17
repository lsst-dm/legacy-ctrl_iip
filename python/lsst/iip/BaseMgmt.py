from time import sleep

class BaseMgmt:

    def __init__(self):


    def ack_timer(self, seconds):
        sleep(seconds)
        return True

