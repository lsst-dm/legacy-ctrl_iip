rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=F1_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=F2_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=F3_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=F4_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=F5_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=F6_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=F7_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=F8_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=F9_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=F10_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=F11_consume

rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=D1_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=D2_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=D3_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=D4_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=D5_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=D6_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=D7_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=D8_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=D9_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=D10_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=D11_consume


rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=distributor_publish
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=dmcs_consume
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=dmcs_publish
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=forwarder_publish
rabbitmqadmin -u DMCS -p DMCS --vhost=/bunny declare queue name=ncsa_publish
