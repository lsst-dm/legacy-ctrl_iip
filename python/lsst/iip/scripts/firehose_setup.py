import pika

#EXCHANGE='message'
#EXCHANGE_TYPE='direct'


connection = pika.BlockingConnection(pika.URLParameters('amqp://adm:adm@141.142.208.191:5672/%2ftester'))

def q_bind_okk():
    pass

channel = connection.channel()

## Bind signature details
## queue_bind(callback, queue, exchange, routing_key=None, nowait=False, arguments=None)

#channel.queue_delete(queue='firehose')
#channel.exchange_delete(exchange='amq.rabbitmq.trace')
#channel.queue_declare(queue='firehose')
channel.queue_declare(queue='firehose',durable=True)
channel.queue_bind(queue='firehose', exchange='amq.rabbitmq.trace', routing_key='firehose' )

connection.close()

#def main():
#    setup = Setup()
#
#if __name__ == '__main__':
#    main()
#
#"""
#while True:
#  x = int(raw_input("1 = forwarder responses, 2 = dmcs responses, 3 = other component, or 4 - F4: "))
#  if x == 1:
