import sys
import time 

sys.path.append("/home/centos/ctrl_iip/python/lsst/iip")

from SimplePublisher import * 

sp = SimplePublisher("amqp://BASE:BASE@141.142.208.241:5672/%2fbunny")

devices = ["AR", "PP", "CU"] 

ar_enable = {} 
ar_enable["MSG_TYPE"] = "ENABLE"
ar_enable["DEVICE"] = "AR"
ar_enable["CMD_ID"] = "13333333333" 
sp.publish_message("ocs_dmcs_consume", ar_enable)

#for dev in devices: 
#    msg = {} 
#    msg["MSG_TYPE"] = "ENABLE"
#    msg["DEVICE"] = dev
#    msg["CMD_ID"] = "100000"
#    sp.publish_message("ocs_dmcs_consume", msg)
#    time.sleep(2)


si = {} 
si["MSG_TYPE"] = "START_INTEGRATION"
si["IMAGE_ID"] = "IMG_1000"
si["DEVICE"] = "AR"
sp.publish_message("ocs_dmcs_consume", si)
time.sleep(2)

