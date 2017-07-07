import pika 

connection = pika.BlockingConnection(pika.URLParameters("amqp://OCS:OCS@141.142.208.241/%2fbunny"))
channel = connection.channel() 

queue_list = [
    "pp_foreman_consume", 
    "f1_consume", 
    "d1_consume", 
    "pp_foreman_ack_publish", 
    "ncsa_consume"] 

exchange_name = "message"
channel.exchange_declare("message")

for q in queue_list: 
    channel.queue_declare(queue=q)
    channel.queue_bind(exchange=exchange_name, queue=q)
