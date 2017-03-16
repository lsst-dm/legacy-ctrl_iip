# OCS_Bridge System descriptions
OCS Bridge takes DDS messages from OpenSplice, converts them to RabbitMq messages and sends them to L1 System. 
 
## How to Run
In OCS machine, 
* Run CommandListener executable in one terminal. CommandListener takes about 3-4 seconds to start. 
* Run EventListener executable in another terminal window. 
* Run AckSubscriber executable in another terminal window. 

### CommandListener.cpp 
  CommandListener listens to command messages(enable, disable, standby...) from OCS system. 

### EventListener.cpp 
  EventListener listens to dm events messages(START_INTEGRATION, NEXT_VISIT, READOUT) from OCS system.

### AckSubscriber.cpp 
  AckSubscriber listens to messages from DMCS and acks back to OCS System.

### OCS_Bridge.cpp 
  OCS_Bridge is the parent of CommandListener and EventListener. It reads the configuration file and sets up the rabbitmq publisher. 

If there are not any executables, run `make` in the directory where `makefile` resides.
`make <component-name>` will generate each individual executable. 
where component-name = CommandListener/EventListener/AckSubscriber    
