# How to run OCS components

## Prerequisites
* SAL environment is installed and configured.  
* [Yaml-CPP v0.5.3](https://github.com/jbeder/yaml-cpp)
* [SimpleAmqpClient v2.4.0](https://github.com/alanxz/SimpleAmqpClient) 
* [Rabbitmq-C v0.8.0](https://github.com/alanxz/rabbitmq-c) for version 2.0+ of RabbitMQ Broker 

## RUN
1. run `./AckSubscriber`, `./CommandListener`, `./EventSubscriber` in 3 different terminals. 

## Descriptions
* AckSubscriber listens to acks from DMCS and ack them back to OCS. 
* CommandListener listens to commands from OCS to DMCS relating to archiver, catchuparchiver and processingcluster. 
* EventSubscriber listens to events from OCS and forwards them to DMCS. 

## Simulation
* To simulate OCS commands for DM devices(AR, CU, PP), the commands are in iip/ocs/commands directory. 
* To simulate OCS commands for Events from TCS, CCS, event commands are in iip/ocs/events directory. 

## Explanation 
Prerequisite softwares(yaml-cpp, rabbitmq-c, SimpleAmqpClient) are built and installed in the `ocs/core` directory. 
The main OCS_Bridge files are located in the `ocs/src` directory. Header files are configured in `ocs/include` directory 
while object files are located in `ocs/obj` directory. `src`, `commands` and `events` directory have their own `makefile`. 
Each makefile can be run independently of the others to generate the executables. Since core softwares are included, all 
makefiles do not depend on /usr/local/lib or /usr/loca/include directories and can be built automatically by using 
the included `makefiles`.

## Running Tests 
In the iip directory, run 

* AckSubscriber  
`pytest -s -v tests/test_ocs_acksubscriber.py`  
AckSubscriber test takes a while to start up since it simulates CommandListener, which takes about 2 minutes to be ready.   

* CommandListener  
`pytest -s -v tests/test_ocs_commandlistener.py` 

* EventSubscriber  
`pytest -s -v tests/test_ocs_eventsubscriber.py`

# Command Sequence 
* STANDBY
* ENABLE
* DISABLE
