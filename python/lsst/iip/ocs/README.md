# How to run OCS components

## Prerequisites
* SAL environment is installed and configured.  
* [Yaml-CPP](https://github.com/jbeder/yaml-cpp)
* [SimpleAmqpClient](https://github.com/alanxz/SimpleAmqpClient) 
* [Rabbitmq-C](https://github.com/alanxz/rabbitmq-c) 

## RUN
1. run `./AckSubscriber`, `./CommandListener`, `./EventSubscriber` in 3 different terminals. 

## Descriptions
* AckSubscriber listens to acks from DMCS and ack them back to OCS. 
* CommandListener listens to commands from OCS to DMCS relating to archiver, catchuparchiver and processingcluster. 
* EventSubscriber listens to events from OCS and forwards them to DMCS. 

## Simulation
* To simulate OCS commands for DM devices(AR, CU, PP), the commands are in iip/ocs/commands directory. 
* To simulate OCS commands for Events from TCS, CCS, event commands are in iip/ocs/sal_events directory. 
