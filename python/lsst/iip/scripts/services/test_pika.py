import pika 

co = pika.BlockingConnection(pika.URLParameters("amqp://DMCS:DMCS@141.142.208.160:5672/%2fbunny_at"))
