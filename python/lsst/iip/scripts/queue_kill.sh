rabbitmqctl purge_queue -p /bunny pp_foreman_consume
rabbitmqctl purge_queue -p /bunny f1_consume
rabbitmqctl purge_queue -p /bunny d1_consume
rabbitmqctl purge_queue -p /bunny pp_foreman_ack_publish
rabbitmqctl purge_queue -p /bunny ncsa_consume
