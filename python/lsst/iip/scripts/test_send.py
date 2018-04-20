import sys 
sys.path.insert(1, "../")
from SimplePublisher import SimplePublisher

sp = SimplePublisher("amqp://DMCS:DMCS@localhost:5672/%2fbunny_at") 
sp2 = SimplePublisher("amqp://DMCS:DMCS@localhost:5672/%2ftest_at") 
msg = { "HELLO": "WORLD" } 
sp.publish_message("f91_consume", msg)
sp2.publish_message("f91_consume", msg)
