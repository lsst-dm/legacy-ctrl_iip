echo "Checking services ..." 

declare -a services=( 
    "DMCS"
    "AuxDevice" 
    "CommandListener"
    "EventSubscriber" 
    "AckSubscriber")

while true; do
    for sv in ${services[@]}; do
        status=$(systemctl is-active ${sv})
        case $status in
            active)
                echo "${sv} is active." 
                ;;
            *)
                echo "Stopping services..."
                systemctl stop DMCS
                systemctl stop AuxDevice
                systemctl stop CommandListener
                systemctl stop EventSubscriber
                systemctl stop AckSubscriber
                echo "Purging queues..."
                /usr/bin/bash ./scripts/at_rmq_purge_queues.sh
                echo "Restarting services..."
                systemctl restart ctrl_iip.target
                sleep 10
                ;; 
        esac
    done
    sleep 10
done
