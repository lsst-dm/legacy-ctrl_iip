#include "Consumer.h"

class AckSubscriber { 
    public: 
        Consumer ack_consumer; 
	AckSubscriber(); 
	~AckSubscriber(); 
	void setup_consumer(); 
	static void on_dmcs_message(boost::python::object ch, boost::python::object method, boost::python::object properties, boost::python::dict dict);
	void run(); 

	string base_broker_addr; 
	string OCS_CONSUME; 
	boost::python::object ocs_consumer; 
}; 

