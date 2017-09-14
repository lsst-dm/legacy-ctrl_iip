import pika 
import yaml

connection = pika.BlockingConnection(pika.URLParameters("amqp://AFM:AFM@141.142.208.209:5672/%2fbunny"))
channel = connection.channel(); 

devices = ["AR", "CU", "PP"] 

# test send Events to OCS

for device in devices: 
    m = {} 
    m["MSG_TYPE"] = "SUMMARY_STATE_EVENT"
    m["DEVICE"] = device
    m["CURRENT_STATE"] = 0
    channel.basic_publish(exchange="message", 
                          routing_key="dmcs_ocs_publish", 
                          body=yaml.dump(m)) 

    m = {} 
    m["MSG_TYPE"] = "RECOMMENDED_SETTINGS_VERSION_EVENT"
#    m["DEVICE"] = device
    m["CFG_KEY"] = device + "-Normal"
    channel.basic_publish(exchange="message", 
                          routing_key="dmcs_ocs_publish", 
                          body=yaml.dump(m)) 

    m = {} 
    m["MSG_TYPE"] = "SETTINGS_APPLIED_EVENT"
    m["DEVICE"] = device
    m["SETTING"] = "Normal"
    m["APPLIED"] = True
    channel.basic_publish(exchange="message", 
                          routing_key="dmcs_ocs_publish", 
                          body=yaml.dump(m)) 

    m = {} 
    m["MSG_TYPE"] = "APPLIED_SETTINGS_MATCH_START_EVENT"
    m["DEVICE"] = device
    m["APPLIED"] = True
    channel.basic_publish(exchange="message", 
                          routing_key="dmcs_ocs_publish", 
                          body=yaml.dump(m)) 
    
    m = {} 
    m["MSG_TYPE"] = "ERROR_CODE_EVENT"
    m["DEVICE"] = device
    m["ERROR_CODE"] = 1002
    channel.basic_publish(exchange="message", 
                          routing_key="dmcs_ocs_publish", 
                          body=yaml.dump(m)) 

