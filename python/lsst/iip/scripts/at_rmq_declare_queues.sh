# Assumptions:
# * DMCS user is created and has admin previleges to both /bunny and /test. 
# * rabbitmqadmin is downloaded and installed in /usr/bin or /usr/local/bin. 

GREEN="\033[32m"
BOLD="\033[1m"
NORM="\033[0m" 

echo "Queue Declarations started ..." 

echo -e "[${GREEN}${BOLD}STATUS${NORM}] Adding Exchanges." 
./rabbitmqadmin declare exchange name=message type=direct durable=true --vhost=/bunny_at -u DMCS -p DMCS
rabbitmqadmin declare exchange name=message type=direct durable=true --vhost=/test_at -u DMCS -p DMCS

declare -a queues=( "at_foreman_consume"
                    "at_foreman_ack_publish"
                    "archive_ctrl_publish"
                    "dmcs_consume"
                    "dmcs_ack_consume"
                    "ocs_dmcs_consume"
                    "dmcs_ocs_publish"
                    "at_forwarder_publish"
                    "f91_consume"
                    "f92_consume"
                    "f93_consume"
                    "fetch_consume_from_f91"
                    "fetch_consume_from_f92"
                    "fetch_consume_from_f93"
                    "format_consume_from_f91"
                    "format_consume_from_f92"
                    "format_consume_from_f93"
                    "forward_consume_from_f91"
                    "forward_consume_from_f92"
                    "forward_consume_from_f93"
                    "ar_foreman_ack_publish"
                    "test_dmcs_ocs_publish")

echo -e "[${GREEN}${BOLD}STATUS${NORM}] Creating queues in vhost bunny_at." 
for i in ${queues[@]}
do
    rabbitmqadmin declare queue name=$i durable=true --vhost=/bunny_at -u DMCS -p DMCS
    rabbitmqadmin declare binding source=message destination_type=queue destination=$i routing_key=$i --vhost=/bunny_at -u DMCS -p DMCS
done

echo -e "[${GREEN}${BOLD}STATUS${NORM}] Creating queues in vhost test_at." 
for i in ${queues[@]}
do
    rabbitmqadmin declare queue name=$i durable=true --vhost=/test_at -u DMCS -p DMCS
    rabbitmqadmin declare binding source=message destination_type=queue destination=$i routing_key=$i --vhost=/test_at -u DMCS -p DMCS
done

echo -e "[${GREEN}${BOLD}STATUS${NORM}] COMPLETE." 
