from const import *
from copy import deepcopy
from toolsmod import get_timestamp
import yaml
import sys


class YamlHandler:
    def __init__(self, callback=None):
        self._consumer_callback = callback

    
    def yaml_callback(self, ch, method, properties, body): 
        """ Decode the message body before consuming
            Setting the consumer callback function
        """
        msgTree = self.toTree(body)
        pydict = self.decode_message(body)
        self._consumer_callback(ch, method, properties, pydict)


    def encode_message(self, dictValue):
        pydict = deepcopy(dictValue)
        yaml_body = yaml.dump(dictValue)
        return yaml_body


    def decode_message(self, body):
        tmpdict = yaml.load(body) 
        return tmpdict


    def print_yaml(self, body):
        print str(body)
