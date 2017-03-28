#include "Consumer.h"

/** Rabbitmq subscriber class to ack back messages from OCS after processing */ 
class AckSubscriber : public OCS_Bridge { 
    public: 
        
        /** Consumer object to listen to messages from rabbitmq */ 
        Consumer* ack_consumer; 

        /** constructor for Rabbitmq ack subscriber to OCS system */ 
	AckSubscriber(); 

        /** destructor of AckSubscriber object */ 
	~AckSubscriber(); 

        /** Set up rabbitmq consumer object */ 
	void setup_consumer(); 

        /** Run rabbitmq IOLoop to listen to messages */ 
	void run(); 

        /** Rabbitmq callback function to parse into Consumer object to listen to messages
          * @param string message body
          */ 
        static void on_message(std::string); 
}; 

