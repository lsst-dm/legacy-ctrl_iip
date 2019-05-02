#! /bin/bash
case $1 in 
    all) 
        cp ../etc/services/*.service /etc/systemd/system
        cp ../etc/services/*.target /etc/systemd/system
        systemctl daemon-reload
	systemctl start l1d-ctrl_iip.target
        ;;
    *)
        cp $1 /etc/systemd/system
        systemctl daemon-reload
        systemctl start $1 
        systemctl status $1
        ;;
esac

