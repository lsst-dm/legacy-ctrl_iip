# add path to PYTHONPATH
import sys
sys.path.insert(0, "/root/src/git/ctrl_iip/python/lsst/iip")

import pika 
from SimplePublisher import *
from toolsmod import * 
import time
import logging 

logging.basicConfig()

sp = SimplePublisher("amqp://OCS:OCS@141.142.208.191:5672/%2fbunny")

m = {} 
m["MSG_TYPE"] = "SUMMARY_STATE"
m["DEVICE"] = "AR"
m["NAME"] = "HELLO"
m["IDENTIFIER"] = "0"
m["TIMESTAMP"] = "HELLO"
m["ADDRESS"] = "1" 
m["CURRENT_STATE"] = "ENABLE"
m["PREVIOUS_STATE"] = "DISABLE"
m["EXECUTING"] = "NOW"
m["COMMANDS_AVAILABLE"] = "A,B"
m["CONFIGURATIONS_AVAILABLE"] = "C,D"
m["PRIORITY"] = "2"
sp.publish_message("dmcs_ocs_publish", m)

m2 = {} 
m2["MSG_TYPE"] = "SUMMARY_STATE"
m2["DEVICE"] = "CU"
m2["NAME"] = "HELLO"
m2["IDENTIFIER"] = "0"
m2["TIMESTAMP"] = "HELLO"
m2["ADDRESS"] = "1" 
m2["CURRENT_STATE"] = "ENABLE"
m2["PREVIOUS_STATE"] = "DISABLE"
m2["EXECUTING"] = "NOW"
m2["COMMANDS_AVAILABLE"] = "A,B"
m2["CONFIGURATIONS_AVAILABLE"] = "C,D"
m2["PRIORITY"] = "2"
sp.publish_message("dmcs_ocs_publish", m2)

m3 = {} 
m3["MSG_TYPE"] = "SUMMARY_STATE"
m3["DEVICE"] = "PP"
m3["NAME"] = "HELLO"
m3["IDENTIFIER"] = "0"
m3["TIMESTAMP"] = "HELLO"
m3["ADDRESS"] = "1" 
m3["CURRENT_STATE"] = "ENABLE"
m3["PREVIOUS_STATE"] = "DISABLE"
m3["EXECUTING"] = "NOW"
m3["COMMANDS_AVAILABLE"] = "A,B"
m3["CONFIGURATIONS_AVAILABLE"] = "C,D"
m3["PRIORITY"] = "2"
sp.publish_message("dmcs_ocs_publish", m3)

m4 = {} 
m4["ERROR_CODE"] = "1" 
m4["PRIORITY"] = "2"
m4["MSG_TYPE"] = "ERROR_CODE"
m4["DEVICE"] = "AR"
sp.publish_message("dmcs_ocs_publish", m4) 


m5 = {} 
m5["ERROR_CODE"] = "1" 
m5["PRIORITY"] = "2"
m5["MSG_TYPE"] = "ERROR_CODE"
m5["DEVICE"] = "CU"
sp.publish_message("dmcs_ocs_publish", m5) 

m6 = {} 
m6["ERROR_CODE"] = "1" 
m6["PRIORITY"] = "2"
m6["MSG_TYPE"] = "ERROR_CODE"
m6["DEVICE"] = "PP"
sp.publish_message("dmcs_ocs_publish", m6) 

m7 = {} 
m7["APPLIED_SETTINGS_MATCHSTART_ISTRUE"] = "1"
m7["PRIORITY"] = "2"
m7["DEVICE"] = "AR"
m7["MSG_TYPE"] = "APPLIED_SETTINGS_MATCHSTART"
sp.publish_message("dmcs_ocs_publish", m7) 

m8 = {} 
m8["APPLIED_SETTINGS_MATCHSTART_ISTRUE"] = "1"
m8["PRIORITY"] = "2"
m8["DEVICE"] = "CU"
m8["MSG_TYPE"] = "APPLIED_SETTINGS_MATCHSTART"
sp.publish_message("dmcs_ocs_publish", m8) 

m9 = {} 
m9["APPLIED_SETTINGS_MATCHSTART_ISTRUE"] = "1"
m9["PRIORITY"] = "2"
m9["DEVICE"] = "PP"
m9["MSG_TYPE"] = "APPLIED_SETTINGS_MATCHSTART"
sp.publish_message("dmcs_ocs_publish", m9) 
