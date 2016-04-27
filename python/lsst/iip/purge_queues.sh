rabbitmqctl -p /bunny purge_queue F1_consume
rabbitmqctl -p /bunny purge_queue F2_consume
rabbitmqctl -p /bunny purge_queue F3_consume
rabbitmqctl -p /bunny purge_queue F4_consume
rabbitmqctl -p /bunny purge_queue F5_consume
rabbitmqctl -p /bunny purge_queue F6_consume
rabbitmqctl -p /bunny purge_queue F7_consume
rabbitmqctl -p /bunny purge_queue F8_consume
rabbitmqctl -p /bunny purge_queue F9_consume
rabbitmqctl -p /bunny purge_queue F10_consume
rabbitmqctl -p /bunny purge_queue F11_consume

rabbitmqctl -p /bunny purge_queue dmcs_consume
rabbitmqctl -p /bunny purge_queue dmcs_publish
rabbitmqctl -p /bunny purge_queue ncsa_publish
