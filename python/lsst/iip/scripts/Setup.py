import pika
import time

#EXCHANGE_TYPE='direct'


class Setup:
    EXCHANGE='message'

    def __init__(self):

        self.connection = pika.BlockingConnection(pika.URLParameters('amqp://PFM:PFM@141.142.208.209:5672/%2fbunny'))
        self.channel = self.connection.channel()

        queue_names = [
                "ar_foreman_consume", 
                "pp_foreman_consume", 
                "cu_foreman_consume", 
                "dmcs_consume", 
                "dmcs_ack_consume", 
                "ocs_dmcs_consume", 
                "event_dmcs_consume", 
                "dmcs_ocs_publish", 
                "ar_forwarder_publish", 
                "pp_forwarder_publish", 
                "cu_forwarder_publish", 
                "f1_consume", 
                "d1_consume", 
                "ar_foreman_ack_publish", 
                "pp_foreman_ack_publish", 
                "cu_foreman_ack_publish", 
                "audit_consume", 
                "archive_ctrl_consume", 
                "archive_ctrl_publish", 
                "ncsa_consume", 
                "ncsa_publish", 
                "ncsa_foreman_ack_publish"] 

        self.channel.exchange_declare(exchange=self.EXCHANGE)

        for q in queue_names: 
            self.channel.queue_declare(queue=q,durable=True)
            self.channel.queue_bind(queue=q, exchange=self.EXCHANGE)

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

    
    
def main():
    setup = Setup()

    print("Rabbit setup complete.")


if __name__ == '__main__':
    main()
