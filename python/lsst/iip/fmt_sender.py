import SimplePublisher
from time import sleep


sp = SimplePublisher("amqp://PFM_PUB:PFM_PUB@141.142.238.10/%2ftest", "YAML") 

msg = {} 
msg["MSG_TYPE"] = "AT_FWDR_HEADER_READY" 
msg["IMAGE_ID"] = "IMG_100"
msg["FILENAME"] = "dave@141.142.238.177:/tmp/header/cam.header"
sp.publish_message("f1_consume", msg) 
sleep(1)

msg = {} 
msg["MSG_TYPE"] = "FORMAT_HEADER_READY" 
msg["IMAGE_ID"] = "IMG_100" 
msg["FILENAME"] = "dave@141.142.238.177:/tmp/header/cam.header"
sp.publish_message("format_consume_from_f1", msg) 
sleep(1)

msg = {} 
msg["MSG_TYPE"] = "FORWARD_END_READOUT"
msg["IMAGE_ID"] = "IMG_100" 
sp.publish_message("forward_consume_from_f1", msg) 
sleep(1)
