import pika
import argparse
from lsst.ctrl.iip.Credentials import Credentials


class Setup:
    def __init__(self, vhost, hostname=None):
        cred = Credentials("iip_cred.yaml")

        user = cred.getUser("service_user")
        passwd = cred.getPasswd("service_passwd")

        host = hostname if hostname else "localhost"

        # TODO: Remove prepending / from vhost name
        url = f"amqp://{user}:{passwd}@{host}/{vhost}"
        connection = pika.BlockingConnection(
            pika.URLParameters(url)
        )
        self.channel = connection.channel()

        self.DEFAULT_QUEUES = [
            "at_foreman_consume",
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
            "telemetry_queue",
            "test_dmcs_ocs_publish"  # optional test queue for dmcs_ocs test
        ]

    def setup(self):
        # declare exchange
        self.channel.exchange_declare(
            exchange='message',
            exchange_type='direct',
            durable=True
        )

        # create queues
        for queue in self.DEFAULT_QUEUES:
            self.channel.queue_declare(queue=queue, durable=True)
            self.channel.queue_bind(
                queue=queue,
                exchange='message',
                routing_key=queue
            )


def main():
    parser = argparse.ArgumentParser(
        description="Create queues for existing vhost. '/' must be passed as \
                '%2f'. Example - /test_at is %2ftest_at "
    )
    parser.add_argument(
        "vhost",
        type=str,
        help="Existing vhost name"
    )
    parser.add_argument(
        "--hostname",
        type=str,
        help="hostname where rabbitmq server is running"
    )

    args = parser.parse_args()
    s = Setup(args.vhost, hostname=args.hostname)
    s.setup()

    print(f"Creating queues for vhost {args.vhost} complete.")


if __name__ == '__main__':
    main()
