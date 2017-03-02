#include <string.h>
#include "SimplePublisher.h"

/** OCS_Bridge handles configuration file opening and setting up publisher for rabbitmq */ 
class OCS_Bridge { 
    public: 
        /** base broker address where rabbitmq server resides in */ 
	std::string base_broker_addr; 
      
        /** publish queue to send messages to DMCS */ 
	std::string OCS_PUBLISH; 

        /** consume queue to listen to messages from DMCS */ 
	std::string OCS_CONSUME; 

        /** SimplePublisher object to send messages to DMCS */ 
        SimplePublisher* ocs_publisher; 

        /** constructor for OCS_Bridge */ 
	OCS_Bridge(); 

        /* destructor for OCS_Bridge */ 
	~OCS_Bridge(); 

        /** create rabbitmq publisher to send messages */ 
	void setup_publisher(); 
}; 
