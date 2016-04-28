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

rabbitmqctl -p /bunny purge_queue D1_consume
rabbitmqctl -p /bunny purge_queue D2_consume
rabbitmqctl -p /bunny purge_queue D3_consume
rabbitmqctl -p /bunny purge_queue D4_consume
rabbitmqctl -p /bunny purge_queue D5_consume
rabbitmqctl -p /bunny purge_queue D6_consume
rabbitmqctl -p /bunny purge_queue D7_consume
rabbitmqctl -p /bunny purge_queue D8_consume
rabbitmqctl -p /bunny purge_queue D9_consume
rabbitmqctl -p /bunny purge_queue D10_consume
rabbitmqctl -p /bunny purge_queue D11_consume


rabbitmqctl -p /bunny purge_queue distributor_publish
rabbitmqctl -p /bunny purge_queue forwarder_publish
rabbitmqctl -p /bunny purge_queue dmcs_consume
rabbitmqctl -p /bunny purge_queue dmcs_publish
rabbitmqctl -p /bunny purge_queue ncsa_publish
