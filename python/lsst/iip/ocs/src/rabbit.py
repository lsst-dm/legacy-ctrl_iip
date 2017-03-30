# add path to PYTHONPATH
import sys
sys.path.insert(0, "/root/src/git/ctrl_iip/python/lsst/iip")

import pika 
from SimplePublisher import *
from toolsmod import * 
import time
import logging 

logging.basicConfig()

Sp = SimplePublisher("amqp://OCS:OCS@141.142.238.160:5672/%2fbunny")
