#! /bin/bash
case $1 in 
    all) 
        cp *.service /etc/systemd/system
        cp *.target /etc/systemd/system
        systemctl daemon-reload
        #systemctl start ctrl_iip.target
        #systemctl status ctrl_iip.target
        ;;
    *)
        cp $1 /etc/systemd/system
        systemctl daemon-reload
        systemctl start $1 
        systemctl status $1
        ;;
esac

