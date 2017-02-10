import sys
import time 

sys.path.append("/home/centos/ctrl_iip/python/lsst/iip")

from SimplePublisher import * 

sp = SimplePublisher("amqp://BASE:BASE@141.142.208.241:5672/%2fbunny")

devices = ["AR", "PP", "CU"] 

ar_enable = {} 
ar_enable["MSG_TYPE"] = "STANDBY"
ar_enable["DEVICE"] = "AR"
ar_enable["CMD_ID"] = "13333333333" 
sp.publish_message("ocs_dmcs_consume", ar_enable)
time.sleep(2)

msg = {} 
msg["MSG_TYPE"] = "ENABLE"
msg["DEVICE"] = "AR"
msg["CMD_ID"] = "1000"
sp.publish_message("ocs_dmcs_consume", msg)
time.sleep(2)

next_visit = {} 
next_visit["MSG_TYPE"] = "NEXT_VISIT"
next_visit["VISIT_ID"] = "AR_200"
next_visit["BORE_SIGHT"] = "TBD"
sp.publish_message("ocs_dmcs_consume", next_visit)
time.sleep(2)

si = {} 
si["MSG_TYPE"] = "START_INTEGRATION"
si["IMAGE_ID"] = "IMG_1000"
si["DEVICE"] = "AR"
sp.publish_message("ocs_dmcs_consume", si)
time.sleep(2)

ro = {} 
ro["MSG_TYPE"] = "READOUT"
ro["IMAGE_ID"] = "IMG_1k17"
ro["DEVICE"] = "AR"
sp.publish_message("ocs_dmcs_consume", ro)
time.sleep(2)
