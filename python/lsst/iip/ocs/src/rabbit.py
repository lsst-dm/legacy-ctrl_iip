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
m["MSG_TYPE"] = "SUMMARY_STATE_EVENT"
m["DEVICE"] = "AR"
m["CURRENT_STATE"] = "0"
sp.publish_message("dmcs_ocs_publish", m)

m2 = {} 
m2["MSG_TYPE"] = "SUMMARY_STATE_EVENT"
m2["DEVICE"] = "CU"
m2["CURRENT_STATE"] = "0"
sp.publish_message("dmcs_ocs_publish", m2)

m3 = {} 
m3["MSG_TYPE"] = "SUMMARY_STATE_EVENT"
m3["DEVICE"] = "PP"
m3["CURRENT_STATE"] = "0"
sp.publish_message("dmcs_ocs_publish", m3)

m4 = {} 
m4["ERROR_CODE"] = "1" 
m4["MSG_TYPE"] = "ERROR_CODE_EVENT"
m4["DEVICE"] = "AR"
sp.publish_message("dmcs_ocs_publish", m4) 


m5 = {} 
m5["ERROR_CODE"] = "1" 
m5["MSG_TYPE"] = "ERROR_CODE_EVENT"
m5["DEVICE"] = "CU"
sp.publish_message("dmcs_ocs_publish", m5) 

m6 = {} 
m6["ERROR_CODE"] = "1" 
m6["MSG_TYPE"] = "ERROR_CODE_EVENT"
m6["DEVICE"] = "PP"
sp.publish_message("dmcs_ocs_publish", m6) 

m7 = {} 
m7["BOOL"] = "true"
m7["DEVICE"] = "AR"
m7["MSG_TYPE"] = "APPLIED_SETTINGS_MATCH_START_EVENT"
sp.publish_message("dmcs_ocs_publish", m7) 

m8 = {} 
m8["BOOL"] = "false"
m8["DEVICE"] = "CU"
m8["MSG_TYPE"] = "APPLIED_SETTINGS_MATCH_START_EVENT"
sp.publish_message("dmcs_ocs_publish", m8) 

m9 = {} 
m9["BOOL"] = "true"
m9["DEVICE"] = "PP"
m9["MSG_TYPE"] = "APPLIED_SETTINGS_MATCH_START_EVENT"
sp.publish_message("dmcs_ocs_publish", m9) 

m10 = {} 
m10["MSG_TYPE"] = "RECOMMENDED_SETTINGS_VERSION_EVENT" 
m10["DEVICE"] = "AR"
m10["CFG_KEY"] = "AR-normal"
sp.publish_message("dmcs_ocs_publish", m10) 

m11 = {} 
m11["MSG_TYPE"] = "RECOMMENDED_SETTINGS_VERSION_EVENT" 
m11["DEVICE"] = "CU"
m11["CFG_KEY"] = "CU-Normal"
sp.publish_message("dmcs_ocs_publish", m11) 

m12 = {} 
m12["MSG_TYPE"] = "RECOMMENDED_SETTINGS_VERSION_EVENT" 
m12["DEVICE"] = "PP"
m12["CFG_KEY"] = "PP-Normal"
sp.publish_message("dmcs_ocs_publish", m12) 

m13 = {} 
m13["MSG_TYPE"] = "SETTINGS_APPLIED_EVENT"
m13["DEVICE"] = "AR" 
m13["SETTING"] = "NORMAL" 
sp.publish_message("dmcs_ocs_publish", m13) 

m14 = {} 
m14["MSG_TYPE"] = "SETTINGS_APPLIED_EVENT"
m14["DEVICE"] = "CU" 
m14["SETTING"] = "NORMAL" 
sp.publish_message("dmcs_ocs_publish", m14) 

m15 = {} 
m15["MSG_TYPE"] = "SETTINGS_APPLIED_EVENT"
m15["DEVICE"] = "AR" 
m15["SETTING"] = "NORMAL" 
sp.publish_message("dmcs_ocs_publish", m15) 
