# Assumptions:
# * DMCS user is created and has admin previleges to both /bunny and /test. 
# * rabbitmqadmin is downloaded and installed in /usr/bin or /usr/local/bin. 

GREEN="\033[32m"
BOLD="\033[1m"
NORM="\033[0m" 

echo "Queue Purging started ..." 

declare -a queues=( "at_foreman_consume"
                    "at_foreman_ack_publish"
                    "archive_ctrl_publish"
                    "dmcs_consume"
                    "dmcs_ack_consume"
                    "dmcs_fault_consume"
                    "ocs_dmcs_consume"
                    "dmcs_ocs_publish"
                    "at_forwarder_publish"
                    "f91_consume"
                    "f92_consume"
                    "f93_consume"
                    "f99_consume"
                    "fetch_consume_from_f91"
                    "fetch_consume_from_f92"
                    "fetch_consume_from_f93"
                    "fetch_consume_from_f99"
                    "format_consume_from_f91"
                    "format_consume_from_f92"
                    "format_consume_from_f93"
                    "format_consume_from_f99"
                    "forward_consume_from_f91"
                    "forward_consume_from_f92"
                    "forward_consume_from_f93"
                    "forward_consume_from_f99"
                    "ar_foreman_ack_publish"
                    "test_dmcs_ocs_publish") # optional test queue for dmcs_ocs test 

for i in ${queues[@]}
do
    #rabbitmqctl purge_queue --vhost=/bunny_at -u DMCS -p DMCS name=$i
    #rabbitmqctl purge_queue --vhost=/test_at -u DMCS -p DMCS name=$i
    rabbitmqctl purge_queue -p /bunny_at $i
    rabbitmqctl purge_queue -p /test_at $i
done

echo -e "[${GREEN}${BOLD}  OK  ${NORM}] COMPLETE." 
