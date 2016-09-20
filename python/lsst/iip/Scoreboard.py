import redis
import time
import sys
import logging

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class Scoreboard:
    """This is the parent class of the three scoreboard classes. 
       It, and they, form an interface for the Redis in-memory DB
       that continually stores state information about components and jobs.
    """

    def persist_snapshot(self, connection, filename):
        LOGGER.info('Saving Scoreboard Snapshot')
        self._redis.config_set("dbfilename", filename + ".rdb")
        while True: 
            try: 
                self._redis.bgsave()
                break
            except: 
                print("Persisting.")
                time.sleep(10) 

    










