rabbitmqctl add_vhost ${VHOST}
rabbitmqctl set_permissions -p ${VHOST} ${RABBITMQ_USER} ".*" ".*" ".*"
python3 rmq_declare_queues.py ${VHOST}
