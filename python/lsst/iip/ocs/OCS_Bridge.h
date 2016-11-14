#include "SAL_dm.h"
#include "ccpp_sal_dm.h"
#include "os.h"
#include "example_main.h"
#include <string.h>
#include <boost/python.hpp>

class OCS_Bridge { 
    public: 
	string base_broker_addr; 
	string DMCS_PUBLISH; 
	string DMCS_CONSUME; 
	boost::python::object dmcs_publisher; 
	boost::python::object dmcs_consumer; 
	OCS_Bridge(string base_broker_addr); 
	void setup_publisher(); 
	void setup_rabbit_consumer(); 
	void setup_ocs_consumer(); 	
	static void *run_dmcs_consumer(void *); 
	static void *run_ocs_consumer(void *); 
	static void on_dmcs_message(boost::python::object, boost::python::object, boost::python::object, string); 
	void run(); 
}; 
