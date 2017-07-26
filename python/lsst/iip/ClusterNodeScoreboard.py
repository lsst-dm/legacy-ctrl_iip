from Scoreboard import Scoreboard
import redis
import logging
from const import * 

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class ClusterNodeScoreboard(Scoreboard):
    CLUSTERNODES_ROWS = 'clusternodes_rows'
    DB_TYPE = ""
    DB_INSTANCE = None
  

    def __init__(self, db_type, db_instance, fdict):
        # Log in
        LOGGER.info('Setting up ClusterNodeScoreboard')
        self.DB_TYPE = db_type
        self.DB_INSTANCE = db_instance
        self._redis = self.connect()
        self._redis.flushdb()

        # Set fields in redis
        cluster_nodes = fdict.keys()
        for node in cluster_nodes:
            fields = fdict[node]
            name = fields['NAME']
            routing_key = fields['CONSUME_QUEUE']
    
            '''
            Fields include: NAME, HOSTNAME, IP_ADDR, CONSUME_QUEUE, STATE,
            STATUS, ROUTING_KEY, JOB_NUM
            '''
            for field in fields:
                self._redis.hset(node, field, fields[field])
                self._redis.hset(node, 'STATE', 'IDLE')
                self._redis.hset(node, 'STATUS', 'HEALTHY')
                self._redis.hset(node, 'ROUTING_KEY', routing_key)
                self._redis.hset(node, 'JOB_NUM', None)
      
            self._redis.lpush(self.CLUSTERNODES_ROWS, node)


    def connect(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=self.DB_INSTANCE)
        return redis.Redis(connection_pool=pool)


    # Return all nodes
    def return_nodes_list(self):
        all_nodes = self._redis.lrange(self.CLUSTERNODES_ROWS, 0, -1)
        return all_nodes


    # Return all nodes
    def return_nodes_with_consume(self):
        all_nodes = self._redis.lrange(self.CLUSTERNODES_ROWS, 0, -1)
        node_dict = {}
        for node in all_nodes:
            name = self._redis.hget(node, 'NAME')
            node_dict[name] = self._redis.hget(node, 'CONSUME_QUEUE')
        return node_dict


    # Return healthy nodes
    # TODO: add communication later
    def return_healthy_nodes_list(self):
        healthy_nodes = []
        nodes = self._redis.lrange(self.CLUSTERNODES_ROWS, 0, -1)
        for node in nodes:
            if self._redis.hget(node, 'STATUS') == 'HEALTHY':
                healthy_nodes.append(node)

        return healthy_nodes


    # Return healthy and idle nodes
    def return_available_nodes_list(self):
        available_nodes = []
        nodes = self._redis.lrange(self.CLUSTERNODES_ROWS, 0, -1)
        for node in nodes:
            if ((self._redis.hget(node, 'STATUS')) == 'HEALTHY') and ((self._redis.hget(node, 'STATE'))  == 'IDLE'):
                available_nodes.append(node)

        return available_nodes


    # Set all node to one status
    def setall_nodes_status(self, status):
        nodes = self._redis.lrange(self.CLUSTERNODES_ROWS, 0, -1)
        for node in nodes:
            self._redis.hset(node, 'STATUS', status)


    # # Set all fields of nodes
    # def set_node_params(self, nodes, params):
    #     for node in nodes:
    #         kees = params.keys()
    #         for kee in kees:
    #             self._redis.hset(node, kee, params[kee])


    # # Get a field of a node
    # def get_value_for_node(self, node, kee):
    #     return self._redis.hget(node, kee)


    # Set the STATE of a node
    def set_node_state(self, node, state):
        self._redis.hset(node, 'STATE', state)


    # Get the STATE of a node
    def get_node_state(self, node):
        state = self._redis.hget(node, 'STATE')
        return state


    # Set the STATUS of a node
    def set_node_status(self, node, status):
        self._redis.hset(node, 'STATUS', status)


    # Get ROUTING_KEY of a node
    def get_routing_key(self, node):
        return self._redis.hget(node,'ROUTING_KEY')


    # Debug use
    def print_all(self):
        all_nodes = self.return_nodes_list()
        for node in all_nodes:
            print node
            print self._redis.hgetall(node)
        print "--------Finished In print_all--------"



