#include "Consumer.h"

class AckSubscriber { 
    public: 
        Consumer* ack_consumer; 
	AckSubscriber(); 
	~AckSubscriber(); 
	void setup_consumer(); 
	void run(); 

        static void on_message(std::string); 

	std::string base_broker_addr; 
	std::string OCS_CONSUME; 
}; 

