import pika

EXCHANGE='message'
EXCHANGE_TYPE='direct'

class Setup:

    #connection = pika.BlockingConnection(pika.URLParameters('amqp://DMCS:DMCS@141.142.208.191:5672/%2fbunny'))


    def __init__(self):
        connection = pika.BlockingConnection(pika.URLParameters('amqp://DMCS:DMCS@141.142.238.160:5672/%2fbunny'))
        channel = connection.channel()

#        channel.exchange_declare(self.on_exchange_declare_ok,'message', 'direct')

        channel.queue_declare(queue='F1_consume')
        channel.queue_declare(queue='F2_consume')
        channel.queue_declare(queue='F3_consume')
        channel.queue_declare(queue='F4_consume')
        channel.queue_declare(queue='F5_consume')
        channel.queue_declare(queue='F6_consume')
        channel.queue_declare(queue='F7_consume')
        channel.queue_declare(queue='F8_consume')
        channel.queue_declare(queue='F9_consume')
        channel.queue_declare(queue='F10_consume')
        channel.queue_declare(queue='F11_consume')

        channel.queue_declare(queue='D1_consume')
        channel.queue_declare(queue='D2_consume')
        channel.queue_declare(queue='D3_consume')
        channel.queue_declare(queue='D4_consume')
        channel.queue_declare(queue='D5_consume')
        channel.queue_declare(queue='D6_consume')
        channel.queue_declare(queue='D7_consume')
        channel.queue_declare(queue='D8_consume')
        channel.queue_declare(queue='D9_consume')
        channel.queue_declare(queue='D10_consume')
        channel.queue_declare(queue='D11_consume')

        channel.queue_declare(queue='forwarder_publish')
        channel.queue_declare(queue='distributor_publish')

        channel.queue_declare(queue='dmcs_consume')
        channel.queue_declare(queue='dmcs_publish')

        channel.queue_declare(queue='ncsa_publish')

        channel.queue_declare(queue='reports')

        connection.close()


    def on_exchange_declare_ok(self, frame):
        pass

def main():
    setup = Setup()

if __name__ == '__main__':
    main()

"""
while True:
  x = int(raw_input("1 = forwarder responses, 2 = dmcs responses, 3 = other component, or 4 - F4: "))
  if x == 1:
    #channel.basic_publish(exchange='',routing_key='forwarder_responses',body='Are you being forward?')
    channel.basic_publish(exchange='message',routing_key='forwarder_publish',body='Are you being forward?')
  elif x == 2:
    #channel2.basic_publish(exchange='',routing_key='from_dmcs',body='From the ding dang DMCS')
    #channel.basic_publish(exchange='',routing_key='example.text',body='From the ding dang DMCS')
    channel.basic_publish(exchange='message',routing_key='dmcs_publish',body='From the ding dang DMCS')
  elif x == 3:
    channel.basic_publish(exchange='message',routing_key='F4_consume',body='Calling F4, calling F4!')
  elif x == 4:
    channel.basic_publish(exchange='message',routing_key='F2_consume',body='Calling F4, calling F4!')
  elif x == 3:
    channel.basic_publish(exchange='message',routing_key='F4_consume',body='Calling F4, calling F4!')
  else:
    channel.basic_publish(exchange='message',routing_key='F11_consume',body='a message to a third party')
    #channel2.basic_publish(exchange='message',routing_key='mainone',body='a message to a third party')
"""


