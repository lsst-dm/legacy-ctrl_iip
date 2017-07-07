import SimplePublisher as ss

sp = ss.SimplePublisher("amqp://AUDIT:AUDIT@141.142.208.241:5672/%2fbunny")

m = {} 
m["MSG_TYPE"] = "START_INTEGRATION"
m["RAFTS"] = [1]
m["JOB_NUM"] = 1
m["ACK_ID"] = "starter_001"
m["VISIT_ID"] = "visit_100"
m["CCDS"] = [100, 101, 102]
sp.publish_message("pp_foreman_consume", m)
