echo "Checking services ..." 

declare -a services=( 
    "l1d-DMCS"
    "l1d-AuxDevice" 
    "l1d-CommandListener"
    "l1d-EventSubscriber" 
    "l1d-AckSubscriber")

while true; do
    for sv in ${services[@]}; do
        status=$(systemctl is-active ${sv})
        case $status in
            active)
                if [ "$1" == "-v" ] 
		then
                    echo "${sv} is running." 
                fi

                STATE=$(redis-cli -n 13 hget AT STATE)
                echo "Data Management System is running." 
                echo "AtArchiver is currently in $STATE state."

                ;;
            *)
                echo "Stopping services..."
                systemctl stop l1d-DMCS
                systemctl stop l1d-AuxDevice
                systemctl stop l1d-CommandListener
                systemctl stop l1d-EventSubscriber
                systemctl stop l1d-AckSubscriber
                echo "Purging queues..."
                /usr/bin/bash ./scripts/at_rmq_purge_queues.sh
                echo "Restarting services..."
                systemctl restart l1d-ctrl_iip.target
                sleep 10
                ;; 
        esac
    done
    sleep 10
done
