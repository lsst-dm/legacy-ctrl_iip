import pika
import time

class Setup:
    def __init__(self):
        credentials = pika.PlainCredentials("DMCS", "DMCS")
        bunny_connection = pika.BlockingConnection(pika.ConnectionParameters(
                                       host="localhost", 
                                       port=5672, 
                                       virtual_host="/bunny_at", 
                                       credentials=credentials))
        bunny_channel = bunny_connection.channel()

        test_connection = pika.BlockingConnection(pika.ConnectionParameters(
                                       host="localhost", 
                                       port=5672, 
                                       virtual_host="/test_at", 
                                       credentials=credentials))
        test_channel = test_connection.channel()

        bunny_channel.exchange_declare(exchange='message', exchange_type='direct', durable=True)
        test_channel.exchange_declare(exchange='message', exchange_type='direct', durable=True)

        queues = ["at_foreman_consume",
                  "at_foreman_ack_publish",
                  "archive_ctrl_publish",
                  "archive_ctrl_consume",
                  "dmcs_consume",
                  "dmcs_ack_consume",
                  "ocs_dmcs_consume",
                  "dmcs_ocs_publish",
                  "dmcs_fault_consume",
                  "gen_dmcs_consume",
                  "at_forwarder_publish",
                  "f91_consume",
                  "f92_consume",
                  "f93_consume",
                  "f99_consume",
                  "fetch_consume_from_f91",
                  "fetch_consume_from_f92",
                  "fetch_consume_from_f93",
                  "fetch_consume_from_f99",
                  "format_consume_from_f91",
                  "format_consume_from_f92",
                  "format_consume_from_f93",
                  "format_consume_from_f99",
                  "forward_consume_from_f91",
                  "forward_consume_from_f92",
                  "forward_consume_from_f93",
                  "forward_consume_from_f99",
                  "f99_consume_from_fetch",
                  "f99_consume_from_format",
                  "f99_consume_from_forward",
                  "ar_foreman_ack_publish",
                  "test_dmcs_ocs_publish"] # optional test queue for dmcs_ocs test ,


        for queue in queues: 
            bunny_channel.queue_declare(queue=queue,durable=True)
            bunny_channel.queue_bind(queue=queue, exchange='message', routing_key=queue )

            test_channel.queue_declare(queue=queue,durable=True)
            test_channel.queue_bind(queue=queue, exchange='message', routing_key=queue )

def main():
    setup = Setup()
    print("Rabbit setup complete.")


if __name__ == '__main__':
    main()
