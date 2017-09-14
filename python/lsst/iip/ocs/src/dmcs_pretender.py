import Consumer 
import yaml
import SimplePublisher 


sp = SimplePublisher.SimplePublisher("amqp://PFM:PFM@141.142.208.209:5672/%2fbunny")
c = Consumer.Consumer("amqp://F1:F1@141.142.208.209:5672/%2fbunny", "ocs_dmcs_consume")

def on_message(ch, method, properties, body): 
    print("=== Received %s" % body)
    d = body
    d["ACK_BOOL"] = True
    d["ACK_STATEMENT"] = "works"
    
    cmd = d["MSG_TYPE"] 
    d["MSG_TYPE"] = cmd + "_ACK"
    print("=== Sent %s" % d)
    sp.publish_message("dmcs_ocs_publish", d)
    

print("=== DMCS running") 
c.run(on_message)
