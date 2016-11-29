#include "SAL_dm.h"
#include "ccpp_sal_dm.h"
#include "os.h"
#include "example_main.h"
#include <string.h>
#include <boost/python.hpp>
#include <SimpleAmqpClient/SimpleAmqpClient.h>

class OCS_Bridge { 
    public: 
	pthread_t consume_thread;
	struct thread_args { 
	    boost::python::object pyObj; 
	    boost::python::object func; 
	    AmqpClient::Channel::ptr_t amqpObj;
	    string broker_addr; 
	    string queue_name; 
	}; 
	struct thread_args *rabbit_consume_args; 
	struct thread_args *ocs_consume_args; 

	OCS_Bridge(string); 
	~OCS_Bridge(); 
	static void process_ocs_message(AmqpClient::Channel::ptr_t, string, string); 

    private: 
	string base_broker_addr; 
	string OCS_PUBLISH; 
	string OCS_CONSUME; 
	AmqpClient::Channel::ptr_t ocs_publisher; 
	boost::python::object ocs_consumer; 

	void setup_publisher(); 
	void setup_rabbit_consumer(); 
	static void *run_dmcs_consumer(void *); 
	static void on_dmcs_message(boost::python::object, boost::python::object, boost::python::object, boost::python::dict); 
}; 
