# Assumptions:
# * DMCS user is created and has admin previleges to both /bunny and /test. 
# * rabbitmqadmin is downloaded and installed in /usr/bin or /usr/local/bin. 

echo "Queue Declarations started ..." 
rabbitmqadmin declare queue name=ar_foreman_consume durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=pp_foreman_consume durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=cu_foreman_consume durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=dmcs_consume durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=dmcs_ack_consume durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=ocs_dmcs_consume durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=event_dmcs_consume durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=dmcs_ocs_publish durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=ar_forwarder_publish durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=pp_forwarder_publish durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=cu_forwarder_publish durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=f1_consume durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=d1_consume durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=ar_foreman_ack_publish durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=pp_foreman_ack_publish durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=cu_foreman_ack_publish durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=audit_consume durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=archive_ctrl_consume durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=archive_ctrl_publish durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=ncsa_consume durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=ncsa_publish durable=true -u DMCS -p DMCS --vhost=/bunny
rabbitmqadmin declare queue name=ncsa_foreman_ack_publish durable=true -u DMCS -p DMCS --vhost=/bunny

rabbitmqadmin declare exchange name=message type=direct durable=true --vhost=/bunny -u DMCS -p DMCS

rabbitmqadmin declare binding source=message destination=ar_foreman_consume --vhost=/bunny -u DMCS -p DMCS 
rabbitmqadmin declare binding source=message destination=pp_foreman_consume --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=cu_foreman_consume --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=dmcs_consume --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=dmcs_ack_consume --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=ocs_dmcs_consume --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=event_dmcs_consume --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=dmcs_ocs_publish --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=ar_forwarder_publish --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=pp_forwarder_publish --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=cu_forwarder_publish --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=f1_consume --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=d1_consume --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=ar_foreman_ack_publish --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=pp_foreman_ack_publish --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=cu_foreman_ack_publish --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=audit_consume --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=archive_ctrl_consume --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=archive_ctrl_publish --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=ncsa_consume --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=ncsa_publish --vhost=/bunny -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=ncsa_foreman_ack_publish --vhost=/bunny -u DMCS -p DMCS

rabbitmqadmin declare queue name=ar_foreman_consume durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=pp_foreman_consume durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=cu_foreman_consume durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=dmcs_consume durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=dmcs_ack_consume durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=ocs_dmcs_consume durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=event_dmcs_consume durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=dmcs_ocs_publish durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=ar_forwarder_publish durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=pp_forwarder_publish durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=cu_forwarder_publish durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=f1_consume durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=d1_consume durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=ar_foreman_ack_publish durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=pp_foreman_ack_publish durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=cu_foreman_ack_publish durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=audit_consume durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=archive_ctrl_consume durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=archive_ctrl_publish durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=ncsa_consume durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=ncsa_publish durable=true -u DMCS -p DMCS --vhost=/test
rabbitmqadmin declare queue name=ncsa_foreman_ack_publish durable=true -u DMCS -p DMCS --vhost=/test

rabbitmqadmin declare exchange name=message type=direct durable=true --vhost=/test -u DMCS -p DMCS

rabbitmqadmin declare binding source=message destination=ar_foreman_consume --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=pp_foreman_consume --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=cu_foreman_consume --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=dmcs_consume --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=dmcs_ack_consume --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=ocs_dmcs_consume --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=event_dmcs_consume --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=dmcs_ocs_publish --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=ar_forwarder_publish --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=pp_forwarder_publish --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=cu_forwarder_publish --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=f1_consume --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=d1_consume --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=ar_foreman_ack_publish --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=pp_foreman_ack_publish --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=cu_foreman_ack_publish --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=audit_consume --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=archive_ctrl_consume --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=archive_ctrl_publish --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=ncsa_consume --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=ncsa_publish --vhost=/test -u DMCS -p DMCS
rabbitmqadmin declare binding source=message destination=ncsa_foreman_ack_publish --vhost=/test -u DMCS -p DMCS

echo "XXX DONE." 
