import pika
import time
import os

#EXCHANGE='message'
#EXCHANGE_TYPE='direct'

#############################################################
## This class creates a connection to Rabbit and then
## creates an exchange and necessary queues for a vhost.
## The exchange and queues created are 'durable'
##
## Note: To use this class, create the new vhost with
## rabbitmqctl first. This class does not add user 
## permissions to the new vhost, as this must be done
## with rabbitmqctl.
##
## Additional Note: Immediately below where the connection
## is made, make certain that the user/passwd combo has
## administrative privs and has permissions in the new vhost.
##############################################################

class TestSetup:

    def __init__(self):
        #self.set_permissions()
        #Choose a connection...
        self.connection = pika.BlockingConnection(pika.URLParameters('amqp://FM:FM@141.142.238.160:5672/%2ftest'))
        #self.connection = pika.BlockingConnection(pika.URLParameters('amqp://adm:adm@141.142.238.160:5672/%2fbunny'))

        self.channel = self.connection.channel()

        ## Bind signature details
        ## queue_bind(callback, queue, exchange, routing_key=None, nowait=False, arguments=None)
        
        ### Exchange Declares - message' is primary exchange for lsst 
        self.channel.exchange_declare(exchange='message', type='direct', durable=True)
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
        self.channel.queue_declare(queue='ar_foreman_consume',durable=True)
        self.channel.queue_bind(queue='ar_foreman_consume', exchange='message', routing_key='ar_foreman_consume' )
        
        self.channel.queue_declare(queue='pp_foreman_consume',durable=True)
        self.channel.queue_bind(queue='pp_foreman_consume', exchange='message', routing_key='pp_foreman_consume' )
        
        self.channel.queue_declare(queue='sp_foreman_consume',durable=True)
        self.channel.queue_bind(queue='sp_foreman_consume', exchange='message', routing_key='sp_foreman_consume' )
        
        self.channel.queue_declare(queue='cu_foreman_consume',durable=True)
        self.channel.queue_bind(queue='cu_foreman_consume', exchange='message', routing_key='cu_foreman_consume' )
        
        
        ## These queues are how the DMCS messages each of its foremen
        self.channel.queue_declare(queue='ar_forwarder_publish',durable=True)
        self.channel.queue_bind(queue='ar_forwarder_publish', exchange='message', routing_key='ar_forwarder_publish' )
        
        self.channel.queue_declare(queue='pp_forwarder_publish',durable=True)
        self.channel.queue_bind(queue='pp_forwarder_publish', exchange='message', routing_key='pp_forwarder_publish' )
        
        self.channel.queue_declare(queue='sp_forwarder_publish',durable=True)
        self.channel.queue_bind(queue='sp_forwarder_publish', exchange='message', routing_key='sp_forwarder_publish' )
        
        self.channel.queue_declare(queue='cu_forwarder_publish',durable=True)
        self.channel.queue_bind(queue='cu_forwarder_publish', exchange='message', routing_key='cu_forwarder_publish' )
        
        
        ## DMCS queues
        self.channel.queue_declare(queue='dmcs_consume',durable=True)
        self.channel.queue_bind(queue='dmcs_consume', exchange='message', routing_key='dmcs_consume' )
        
        self.channel.queue_declare(queue='dmcs_ack_consume',durable=True)
        self.channel.queue_bind(queue='dmcs_ack_consume', exchange='message', routing_key='dmcs_ack_consume' )
        
        self.channel.queue_declare(queue='ocs_dmcs_consume',durable=True)
        self.channel.queue_bind(queue='ocs_dmcs_consume', exchange='message', routing_key='ocs_dmcs_consume' )
        
        self.channel.queue_declare(queue='event_dmcs_consume',durable=True)
        self.channel.queue_bind(queue='event_dmcs_consume', exchange='message', routing_key='event_dmcs_consume' )
        
        """ 
        ## Catch all queues for forwarders messaging non-ack info to foremen
        self.channel.queue_declare(queue='ar_forwarder_publish',durable=True)
        self.channel.queue_bind(queue='ar_forwarder_publish', exchange='message',routing_key='ar_forwarder_publish')
        
        self.channel.queue_declare(queue='pp_forwarder_publish',durable=True)
        self.channel.queue_bind(queue='pp_forwarder_publish', exchange='message',routing_key='pp_forwarder_publish')
        
        self.channel.queue_declare(queue='cu_forwarder_publish',durable=True)
        self.channel.queue_bind(queue='cu_forwarder_publish', exchange='message',routing_key='cu_forwarder_publish')
        """
        
        ## Acks to foremen
        self.channel.queue_declare(queue='ar_foreman_ack_publish',durable=True)
        self.channel.queue_bind(queue='ar_foreman_ack_publish', exchange='message', routing_key='ar_foreman_ack_publish' )
        
        self.channel.queue_declare(queue='pp_foreman_ack_publish',durable=True)
        self.channel.queue_bind(queue='pp_foreman_ack_publish', exchange='message', routing_key='pp_foreman_ack_publish' )
        
        self.channel.queue_declare(queue='sp_foreman_ack_publish',durable=True)
        self.channel.queue_bind(queue='sp_foreman_ack_publish', exchange='message', routing_key='sp_foreman_ack_publish' )
        
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
         
        self.channel.queue_declare(queue='ncsa_foreman_ack_publish',durable=True)
        self.channel.queue_bind(queue='ncsa_foreman_ack_publish', exchange='message',routing_key='ncsa_foreman_ack_publish')
         
        self.connection.close()


    def setup_forwarders(self, num):
        for i in range (1, num + 1):
            q = 'f' + str(i) + '_consume'
            self.channel.queue_declare(queue=q,durable=True)
            self.channel.queue_bind(queue=q, exchange='message',routing_key=q)

        
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

    """
    def set_permissions(self):
       os.system('rabbitmqctl -p /test BASE '.*' '.*' '.*') 
       os.system('rabbitmqctl -p /test BASE_PUB '.*' '.*' '.*') 
    
       os.system('rabbitmqctl -p /test AFM '.*' '.*' '.*') 
       os.system('rabbitmqctl -p /test AFM_PUB '.*' '.*' '.*') 
    
       os.system('rabbitmqctl -p /test PFM '.*' '.*' '.*') 
       os.system('rabbitmqctl -p /test PFM_PUB '.*' '.*' '.*') 
    
       os.system('rabbitmqctl -p /test PFM_NCSA '.*' '.*' '.*') 
       os.system('rabbitmqctl -p /test PFM_NCSA_PUB '.*' '.*' '.*') 
    
       os.system('rabbitmqctl -p /test ARCHIE '.*' '.*' '.*') 
       os.system('rabbitmqctl -p /test ARCHIE_PUB '.*' '.*' '.*') 
    
       os.system('rabbitmqctl -p /test AUDIT '.*' '.*' '.*') 
    
       os.system('rabbitmqctl -p /test DMCS '.*' '.*' '.*') 
       os.system('rabbitmqctl -p /test DMCS_PUB '.*' '.*' '.*') 
    
       os.system('rabbitmqctl -p /test NCSA '.*' '.*' '.*') 
       os.system('rabbitmqctl -p /test NCSA_PUB '.*' '.*' '.*') 
    """
    
    
def main():
    print("Starting TestSetup run...")
    setup = TestSetup()

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
