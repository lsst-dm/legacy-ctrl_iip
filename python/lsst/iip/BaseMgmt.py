from time import sleep
import os
import threading

class BaseMgmt:

    shutdown_event = threading.Event()
    shutdown_event.clear()


    def ack_timer(self, seconds):
        sleep(seconds)
        return True

    def shutdown(self):
        shutdown_event.set()
        os.exit(0)

    def progressive_ack_timer(self, func, ack_id, expected_replies, seconds):
        # func should be ACK_SCBD.get_components_for_timed_ack
        counter = 0.0
        while (counter < seconds):
            counter += 0.5
            sleep(0.5)
            response = self.func(ack_id)
            if response == None:
                continue
            if len(list(response.keys())) == expected_replies:
                return response

        response = self.func(ack_id)
        if response == None:
            return None
        elif len(list(response.keys())) == expected_replies:
            return response
        else:
            return None

