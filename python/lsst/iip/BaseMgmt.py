from time import sleep

class BaseMgmt:

    def __init__(self):
        pass


    def ack_timer(self, seconds):
        sleep(seconds)
        return True

