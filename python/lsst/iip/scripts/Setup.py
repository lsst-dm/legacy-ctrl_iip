import pika
import time

#EXCHANGE='message'
#EXCHANGE_TYPE='direct'


class Setup:

    def __init__(self):

        #Choose a connection...
#        self.connection = pika.BlockingConnection(pika.URLParameters('amqp://adm:adm@141.142.208.191:5672/%2fbunny'))
        self.connection = pika.BlockingConnection(pika.URLParameters('amqp://FM:FM@141.142.238.10:5672/%2fbunny'))
        #self.connection = pika.BlockingConnection(pika.URLParameters('amqp://FM:FM@141.142.238.10:5672/%2ftest'))
        #self.connection = pika.BlockingConnection(pika.URLParameters('amqp://adm:adm@141.142.238.160:5672/%2fbunny'))
        #self.connection = pika.BlockingConnection(pika.URLParameters('amqp://adm:adm@141.142.238.160:5672/%2ftester'))

        self.channel = self.connection.channel()
        ## Bind signature details
        ## queue_bind(callback, queue, exchange, routing_key=None, nowait=False, arguments=None)
        
        ### Exchange Declares - message' is primary exchange for lsst 
        self.channel.exchange_declare(exchange='message', exchange_type='direct', durable=True)
        #self.channel.exchange_delete(exchange='message')
        time.sleep(2)
                 
        ## Set up queues for each forwarder and distributor...
        ## start with pool of queues for 40 forwarders and 24 distributors
        #self.delete_forwarder_queues(30)
        #self.delete_distributor_queues(24)
        self.setup_forwarders(30)        
        self.setup_distributors(24)        
        
        ### Queue Declares and Bindings
        
        ## Queue for foreman test suite
        self.channel.queue_declare(queue='f_consume',durable=True)
        self.channel.queue_bind(queue='f_consume', exchange='message', routing_key='f_consume' )
        
        
        ## These queues are how the DMCS messages each of its foremen
        self.channel.queue_declare(queue='ar_foreman_consume',durable=True)
        self.channel.queue_bind(queue='ar_foreman_consume', exchange='message', routing_key='ar_foreman_consume' )
        
        self.channel.queue_declare(queue='pp_foreman_consume',durable=True)
        self.channel.queue_bind(queue='pp_foreman_consume', exchange='message', routing_key='pp_foreman_consume' )
        
        self.channel.queue_declare(queue='cu_foreman_consume',durable=True)
        self.channel.queue_bind(queue='cu_foreman_consume', exchange='message', routing_key='cu_foreman_consume' )
        """
        
        ## DMCS queues
        self.channel.queue_declare(queue='dmcs_fault_queue',durable=True)
        self.channel.queue_bind(queue='dmcs_fault_queue', exchange='message', routing_key='dmcs_fault_queue' )
        """
        self.channel.queue_declare(queue='dmcs_consume',durable=True)
        self.channel.queue_bind(queue='dmcs_consume', exchange='message', routing_key='dmcs_consume' )
        
        self.channel.queue_declare(queue='dmcs_ack_consume',durable=True)
        self.channel.queue_bind(queue='dmcs_ack_consume', exchange='message', routing_key='dmcs_ack_consume' )
        
        self.channel.queue_declare(queue='ocs_dmcs_consume',durable=True)
        self.channel.queue_bind(queue='ocs_dmcs_consume', exchange='message', routing_key='ocs_dmcs_consume' )
        
        self.channel.queue_declare(queue='event_dmcs_consume',durable=True)
        self.channel.queue_bind(queue='event_dmcs_consume', exchange='message', routing_key='event_dmcs_consume' )
        
        
        ## Catch all queues for forwarders messaging non-ack info to foremen
        self.channel.queue_declare(queue='ar_forwarder_publish',durable=True)
        self.channel.queue_bind(queue='ar_forwarder_publish', exchange='message',routing_key='ar_forwarder_publish')
        
        self.channel.queue_declare(queue='pp_forwarder_publish',durable=True)
        self.channel.queue_bind(queue='pp_forwarder_publish', exchange='message',routing_key='pp_forwarder_publish')
        
        self.channel.queue_declare(queue='cu_forwarder_publish',durable=True)
        self.channel.queue_bind(queue='cu_forwarder_publish', exchange='message',routing_key='cu_forwarder_publish')
        
        
        ## Acks to foremen
        self.channel.queue_declare(queue='ar_foreman_ack_publish',durable=True)
        self.channel.queue_bind(queue='ar_foreman_ack_publish', exchange='message', routing_key='ar_foreman_ack_publish' )
        
        self.channel.queue_declare(queue='pp_foreman_ack_publish',durable=True)
        self.channel.queue_bind(queue='pp_foreman_ack_publish', exchange='message', routing_key='pp_foreman_ack_publish' )
        
        self.channel.queue_declare(queue='cu_foreman_ack_publish',durable=True)
        self.channel.queue_bind(queue='cu_foreman_ack_publish', exchange='message', routing_key='cu_foreman_ack_publish' )
        
        
        ## Queues for Archive Controller and Auditor
        self.channel.queue_declare(queue='audit_consume',durable=True)
        self.channel.queue_bind(queue='audit_consume', exchange='message', routing_key='audit_consume' )
        
        self.channel.queue_declare(queue='archive_ctrl_consume',durable=True)
        self.channel.queue_bind(queue='archive_ctrl_consume', exchange='message',routing_key='archive_ctrl_consume')
        
        self.channel.queue_declare(queue='archive_ctrl_publish',durable=True)
        self.channel.queue_bind(queue='archive_ctrl_publish', exchange='message',routing_key='archive_ctrl_publish')
               
        self.channel.queue_declare(queue='dmcs_ocs_publish',durable=True)
        self.channel.queue_bind(queue='dmcs_ocs_publish', exchange='message', routing_key='dmcs_ocs_publish' )
        self.channel.queue_declare(queue='ncsa_consume',durable=True)
        self.channel.queue_bind(queue='ncsa_consume', exchange='message',routing_key='ncsa_consume')
        self.connection.close()


    def setup_forwarders(self, num):
        for i in range (1, num + 1):
            q = 'f' + str(i) + '_consume'
            self.channel.queue_declare(queue=q,durable=True)
            self.channel.queue_bind(queue=q, exchange='message',routing_key=q)
            r = 'f' + str(i) + '_consume_image_name'
            self.channel.queue_declare(queue=r,durable=True)
            self.channel.queue_bind(queue=r, exchange='message',routing_key=r)

        
    def setup_distributors(self, num):
        for i in range (1, num + 1):
            q = 'd' + str(i) + '_consume'
            self.channel.queue_declare(queue=q,durable=True)
            self.channel.queue_bind(queue=q, exchange='message',routing_key=q)

    
    def delete_forwarder_queues(self, num):
        for i in range (1, num + 1):
            q = 'f' + str(i) + '_consume'
            self.channel.queue_delete(queue=q)

        
    def delete_distributor_queues(self, num):
        for i in range (1, num + 1):
            q = 'd' + str(i) + '_consume'
            self.channel.queue_delete(queue=q)

    
    
def main():
    setup = Setup()

    print("Rabbit setup complete.")


if __name__ == '__main__':
    main()

#"""
#while True:
#  x = int(raw_input("1 = forwarder responses, 2 = dmcs responses, 3 = other component, or 4 - F4: "))
#  if x == 1:
#
#self.channel.queue_declare(queue='ack_publish',durable=True)
#self.channel.queue_declare(queue='dmcs_consume',durable=True)
#self.channel.queue_declare(queue='dmcs_consume')
#self.channel.queue_declare(queue='f_consume')
#self.channel.queue_declare(queue='forwarder_publish')
#self.channel.queue_declare(queue='audit_consume')
#self.channel.queue_bind(queue='dmcs_consume', exchange='message', routing_key='dmcs_consume' )
#self.channel.queue_bind(queue='f_consume', exchange='message', routing_key='f_consume' )
#self.channel.queue_bind(queue='forwarder_publish', exchange='message', routing_key='forwarder_publish' )
#self.channel.queue_bind(queue='audit_consume', exchange='message', routing_key='audit_consume' )
#
#self.channel.queue_delete(queue='dmcs_consume')
#self.channel.queue_delete(queue='f_consume')
#self.channel.queue_delete(queue='forwarder_publish')
#self.channel.queue_delete(queue='F_consume')
#time.sleep(2)
#self.channel.exchange_delete(exchange='amq.rabbitmq.trace')
#self.channel.queue_declare(queue='firehose')
