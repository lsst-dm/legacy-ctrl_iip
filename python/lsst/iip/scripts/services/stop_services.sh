#! /bin/bash 
/bin/bash /home/centos/src/git/ctrl_iip/python/lsst/iip/scripts/at_rmq_purge_queues.sh
/bin/systemctl restart ctrl_iip.target
