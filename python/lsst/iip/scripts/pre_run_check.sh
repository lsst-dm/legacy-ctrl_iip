#!/bin/bash
ACTIVE="active"
VAR1="$(systemctl is-active rabbitmq-server.service)"
if [ "$VAR1" == "$ACTIVE" ]
then
    echo "rabbitmq-server is working"
else
    echo "rabbitmq-server is NOT working"
    exit
fi


VAR2="$(systemctl is-active l1d-rabbitmq.service)"
if [ "$VAR2" = "active" ]
then
    echo "rabbitmq.service is working"
else
    echo "rabbitmq.service is NOT working"
    exit
fi


VAR3="$(systemctl is-active l1d-redis.service)"
if [ "$VAR3" = "active" ]
then
    echo "l1d-redis.service is working"
else
    echo "l1d-redis.service is NOT working"
    exit
fi


VAR4="$(systemctl is-active l1d-AckSubscriber.service)"
if [ "$VAR4" = "active" ]
then
    echo "l1d-AckSubscriber.service is working"
else
    echo "l1d-AckSubscriber.service is NOT working"
    exit
fi


VAR5="$(systemctl is-active l1d-EventSubscriber.service)"
if [ "$VAR5" = "active" ]
then
    echo "l1d-EventSubscriber.service is working"
else
    echo "l1d-EventSubscriber.service is NOT working"
    exit
fi


VAR6="$(systemctl is-active l1d-CommandListener.service)"
if [ "$VAR6" = "active" ]
then
    echo "l1d-CommandListener.service is working"
else
    echo "l1d-CommandListener.service is NOT working"
    exit
fi


VAR7="$(systemctl is-active l1d-DMCS.service)"
if [ "$VAR7" = "active" ]
then
    echo "l1d-DMCS.service is working"
else
    echo "l1d-DMCS.service is NOT working"
    exit
fi


VAR8="$(systemctl is-active l1d-AuxDevice.service)"
if [ "$VAR7" = "active" ]
then
    echo "l1d-AuxDevice.service is working"
else
    echo "l1d-AuxDevice.service is NOT working"
    exit
fi



echo "A bunch of stuff"


