import redis
import yaml
import logging
from Scoreboard import Scoreboard

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class AckScoreboard(Scoreboard):
    """Extends parent Scoreboard class and provides initialization
       for Redis ack table, each row being a new timed ack.

       As seen as in the first class variable below, when the 
       connection to Redis is opened, the Ack scoreboard is 
       assigned to Redis's Database instance 3. Redis launches with a default 
       15 separate database instances.
    """

    ### FIX: Put Redis DB numbers in Const
    ACK_SCOREBOARD_DB = 3
    JOBS = 'jobs'
    TIMED_ACK_ID = 'TIMED_ACK_ID'
    JOB_NUM = 'JOB_NUM'
    WORKER_NUM = 'worker_num'
    RAFTS = 'RAFTS'
    STATE = 'STATE'
  

    def __init__(self):
      """After connecting to the Redis database instance 
         ACK_SCOREBOARD_DB, this redis database is flushed 
         for a clean start. A 'charge_database' method is 
         included for testing the module.

         A new row will be added for each TIMED_ACK_ID. This will be
         done as follows:
         1) When a new TIMED_ACK_ID is encountered, row will be added with new ID as string identifier
         2) a list of hashes will be set up for each key/value pair in the message
         3) As new acks with a particular TIMED_ACK_ID are received, the data is added to that row.
         4) After a timer event elapses, the scoreboard is locked and checked  to see which ACKs were received.
      """
      LOGGER.info('Setting up AckScoreboard')
      self._redis = self.connect()
      self._redis.flushdb()
      #DEBUG_ONLY:
      #self.charge_database()
    

    def connect(self):
      pool = redis.ConnectionPool(host='localhost', port=6379, db=self.ACK_SCOREBOARD_DB)
      return redis.Redis(connection_pool=pool) 


    def check_connection(self):
      ok_flag = False
      for i in range (1,4):
        try:
          response = self._redis.client_list()
          ok_flag = True
          break
        except redis.ConnectionError:
          self.connect()

      if ok_flag:
        if i == 1:
          return True
        else:
          LOGGER.info('In ACK Scoreboard, had to reconnect to Redis - all set now')
          return True
      else: 
        LOGGER.info('In ACK Scoreboard, could not reconnect to Redis after 3 attempts')
        return False



    def add_timed_ack(self, ack_msg_body):
      """The first time that a new TIMED_ACK_ID is encountered, the ACK row is created.
         From then on, new ACKS for a particulat ACK_ID are added here. 

         :param str job_number: Necessary for all CRUDs on this new row.
         :param int rafts: The number of 'sub-jobs' to be handled within a job.
         :params str xfer_app: This is the application to be used when 
          transferring a file. This row value is mutable up until the 'READOUT'
          state is entered. Note: This param is for TESTING.
         :param str xfer_file: The file to be transferred from Forwarder to
          to distributor. This value is mutable up until 'READOUT'. Note: this 
          value is also for testing.
      """
      ack_id_string = ack_msg_body[TIMED_ACK]
      
      if self.check_connection():
        self._redis.hset(ack_id_string, ack_msg_body[COMPONENT_NAME], ack_msg_body[ACK_BOOL])
        #self.persist_snapshot()
      else:
        LOGGER.error('Unable to add new ACK; Redis connection unavailable')


    def get_components_for_timed_ack(self, timed_ack):
        """Return components who checked in successfully for a specific job number.

           :param str timed_ack: The the name of the ACK name to be checked.
           :rtype dict
        """
        if self.check_connection():
            component_dict = {}
            keys = self._redis.hkeys(timed_ack)
            for key in keys:
                component_dict[key] = hget(timed_ack, key)

        return component_dict

######### DELETE_BELOW

    def get_value_for_job(self, job_number, kee):
      """Return a value for a specific field.

         :param str job_number: The job in which field value is needed.
         :param str kee: The name of the field to retrieve desired data.
      """
      if self.check_connection():
        return self._redis.hget(str(job_number), kee)
      else:
        return None



    def delete_job(self, job_number):
      #self._redis.hdel(self.JOBS, str(job_number))
      self._redis.lrem(self.JOBS, 0, str(job_number))


    def print_all(self):
      jobs = self._redis.lrange(self.JOBS, 0, -1)
      for job in jobs:
        x = self._redis.hgetall(job)
        print x


    def charge_database(self):
      pairs = {}
      other_pairs = {}
      #pairs = { 'F1':'D2', 'F2':'D6', 'F3':'D11', 'F4':'D1', 'F5':'D7'}
      pairs['F1'] = 'D2'
      pairs['F2'] = 'D6'
      pairs['F3'] = 'D11'
      pairs['F4'] = 'D1'
      pairs['F5'] = 'D7'
      other_pairs = { 'F1':'D10', 'F2':'D1', 'F3':'D11', 'F4':'D8', 'F5':'D4'}

      self.add_job(1,7,'ssh', '1k.test')
      self.add_job(2, 11,'rsync', '193k.test')
      self.add_job(3,1,'ftp', '16.7meg.test')
      self.add_job(4,7,'ssh', '1k.test')
      self.add_job(5, 11,'rsync', '193k.test')
      self.add_job(6,1,'ftp', '16.7meg.test')

      #self.set_pairs_for_job('1',  pairs)
      #self.set_pairs_for_job('2',  pairs)
      self.set_value_for_job('1', 'PAIRS', pairs)
      self.set_value_for_job('4', 'PAIRS', pairs)
      #self.set_value_for_job('5', 'PAIRS', pairs)
      #self.set_value_for_job('6', 'PAIRS', other_pairs)

      #keez = pairs.keys()
      #print("printing just keez")
      #print keez
      Ps = self.get_value_for_job(str(1), 'PAIRS')
      ppps = eval(Ps)
      print "final line"
      print ppps == pairs

def main():
  jbs = JobScoreboard()
  #Ps = jbs.get_value_for_job(str(1), 'PAIRS')
  #print "printing Ps"
  #print Ps
  #ppps = eval(Ps)
  #pps = ppps.keys()
  #print "final line"
  #print ppps == pairs



if __name__ == "__main__": main()
