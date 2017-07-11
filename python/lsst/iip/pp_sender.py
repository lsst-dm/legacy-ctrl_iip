import SimplePublisher as ss
import time

sp = ss.SimplePublisher("amqp://AUDIT:AUDIT@141.142.208.241:5672/%2fbunny")

m = {} 
m["MSG_TYPE"] = "START_INTEGRATION"
m["JOB_NUM"] = 1
m["ACK_ID"] = "starter_001"
m["VISIT_ID"] = "visit_100"
m["SESSION_ID"] = "session_001"
m["CCD_LIST"] = [100]
sp.publish_message("pp_foreman_consume", m)
time.sleep(40)

l = {} 
l["MSG_TYPE"] = "READOUT"
l["JOB_NUM"] = 1
sp.publish_message("pp_foreman_consume", l)

