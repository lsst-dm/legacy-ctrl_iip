for i in {1..5}; do
    x =  "CL"$i;
    echo "rabbitmqctl add_user $x $x"
    #`rabbitmqctl set_permissions -p /scr $x '.*' '.*' '.*'`;
    #rabbitmqctl set_permissions -p /bunny $x \'.\*\' \'.\*\' \'.\*\'
    done
