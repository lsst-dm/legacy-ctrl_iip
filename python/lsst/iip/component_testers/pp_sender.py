import sys
sys.path.append("/home/centos/ctrl_iip/python/lsst/iip")
import SimplePublisher as sp 

publisher = sp.SimplePublisher("amqp://AUDIT:AUDIT@141.142.208.209:5672/%2fbunny")

m = {} 
m["MSG_TYPE"] = "START_INTEGRATION"
m["JOB_NUM"] = "job_100"
m["IMAGE_ID"] = "img_100"
m["VISIT_ID"] = "visit_100"
m["SESSION_ID"] = "session_100"
m["CCD_LIST"] = ["100"]
m["RAFTS"] = "m_100"
m["RESPONSE_QUEUE"] = "pp_foreman_ack_publish"
m["ACK_ID"] = "START_INTEGRATION_ACK_000001" 
publisher.publish_message("pp_foreman_consume", m)
