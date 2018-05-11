
GREEN="\033[32m"
BOLD="\033[1m"
NORM="\033[0m" 

echo -e "Creating Users in rabbitmq..." 
echo -e "[${GREEN}${BOLD}STATUS${NORM}] Adding vhosts." 
rabbitmqctl add_vhost /bunny_at
rabbitmqctl add_vhost /test_at

declare -a users=("BASE"
                  "BASE_PUB"
                  "AUX"
                  "AUX_PUB"
                  "DMCS"
                  "DMCS_PUB"
                  "DMCS_FAULT_PUB"
                  "OCS"
                  "OCS_PUB"
                  "F91"
                  "F92"
                  "F93" 
                  "F91_PUB"
                  "F92_PUB"
                  "F93_PUB"
                  "F91_FETCH_PUB"
                  "F92_FETCH_PUB"
                  "F93_FETCH_PUB"
                  "F91_FORMAT_PUB"
                  "F92_FORMAT_PUB"
                  "F93_FORMAT_PUB"
                  "F91_FORWARD_PUB"
                  "F92_FORWARD_PUB"
                  "F93_FORWARD_PUB"
                  "FETCH_F91"
                  "FETCH_F92"
                  "FETCH_F93"
                  "FETCH_F91_PUB"
                  "FETCH_F92_PUB"
                  "FETCH_F93_PUB"
                  "FORMAT_F91"
                  "FORMAT_F92"
                  "FORMAT_F93"
                  "FORMAT_F91_PUB"
                  "FORMAT_F92_PUB"
                  "FORMAT_F93_PUB"
                  "FORWARD_F91"
                  "FORWARD_F92"
                  "FORWARD_F93"
                  "FORWARD_F91_PUB"
                  "FORWARD_F92_PUB"
                  "FORWARD_F93_PUB") 

echo -e "[${GREEN}${BOLD}STATUS${NORM}] Creating forwarder users." 
for i in ${users[@]}
do
    rabbitmqctl add_user $i $i
    rabbitmqctl set_permissions -p /bunny_at $i ".*" ".*" ".*" 
    rabbitmqctl set_permissions -p /test_at $i ".*" ".*" ".*" 
done

echo -e "[${GREEN}${BOLD}STATUS${NORM}] Creating OCS command users." 
for i in {1..25}; 
do 
   x="CL_"$i; 
   rabbitmqctl add_user $x $x;
   rabbitmqctl set_permissions -p /bunny_at $x ".*" ".*" ".*"
   rabbitmqctl set_permissions -p /test_at $x ".*" ".*" ".*"
done

echo -e "[${GREEN}${BOLD}STATUS${NORM}] Creating OCS event users." 
for i in {1..25}; 
do 
   x="EVN_"$i; 
   rabbitmqctl add_user $x $x;
   rabbitmqctl set_permissions -p /bunny_at $x ".*" ".*" ".*"
   rabbitmqctl set_permissions -p /test_at $x ".*" ".*" ".*"
done

