# Example command sequence
USER=$1
PASSWD=$2
VHOST=$3
rabbitmqctl add_user ${USER} ${PASSWD}
rabbitmqctl add_vhost ${VHOST}
rabbitmqctl set_permissions -p ${VHOST} ${USER} ".*" ".*" ".*"
