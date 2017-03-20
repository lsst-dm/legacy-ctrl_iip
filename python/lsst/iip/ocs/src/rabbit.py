import pika 

connection = pika.BlockingConnection(pika.URLParameters("amqp://ocs:ocs@141.142.208.241/%2fbunny"))
channel = connection.channel()

channel.exchange_declare("message")
channel.queue_declare(queue="test")
channel.queue_bind(queue="test", exchange="message") 

connection.close() 
