# Assumptions:
# * DMCS user is created and has admin previleges to both /bunny and /test. 
# * rabbitmqadmin is downloaded and installed in /usr/bin or /usr/local/bin. 

echo "Queue Declarations started ..." 

#rabbitmqadmin declare exchange name=message type=direct durable=true --vhost=/bunny -u DMCS -p DMCS
#rabbitmqadmin declare exchange name=message type=direct durable=true --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare exchange name=message type=direct durable=true --vhost=/test_hk -u DMCS -p DMCS
declare -a queues=( "ar_foreman_consume"
                    "pp_foreman_consume"
                    "cu_foreman_consume"
                    "dmcs_consume"
                    "dmcs_ack_consume"
                    "ocs_dmcs_consume"
                    "event_dmcs_consume"
                    "dmcs_ocs_publish"
                    "ar_forwarder_publish"
                    "pp_forwarder_publish"
                    "cu_forwarder_publish"
                    "f1_consume"
                    "d1_consume"
                    "ar_foreman_ack_publish"
                    "pp_foreman_ack_publish"
                    "cu_foreman_ack_publish"
                    "audit_consume"
                    "archive_ctrl_consume"
                    "archive_ctrl_publish"
                    "ncsa_consume"
                    "ncsa_publish"
                    "ncsa_foreman_ack_publish") 

for i in ${queues[@]}
do
    #rabbitmqadmin declare queue name=$i durable=true --vhost=/bunny -u DMCS -p DMCS
    #rabbitmqadmin declare binding source=message destination_type=queue destination=$i routing_key=$i --vhost=/bunny -u DMCS -p DMCS

    #rabbitmqadmin declare queue name=$i durable=true --vhost=/test -u DMCS -p DMCS
    #rabbitmqadmin declare binding source=message destination_type=queue destination=$i routing_key=$i --vhost=/test -u DMCS -p DMCS

    rabbitmqadmin declare queue name=$i durable=true --vhost=/test_hk -u DMCS -p DMCS
    rabbitmqadmin declare binding source=message destination_type=queue destination=$i routing_key=$i --vhost=/test_hk -u DMCS -p DMCS
done

echo "XXX DONE." 
