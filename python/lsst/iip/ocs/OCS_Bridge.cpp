#include <pthread.h>
#include <stdio.h> 
#include <string.h>
#include <sstream>
#include <iostream>
#include "OCS_Bridge.h"

using namespace DDS;
using namespace dm;
using namespace std; 
using namespace boost::python;

/* entry point exported and demangled so symbol can be found in shared library */
extern "C" { 
    OS_API_EXPORT
    void *run_ocs_consumer(void *);
}

OCS_Bridge::OCS_Bridge(string base_broker_addr) { 
    this->base_broker_addr = base_broker_addr; 
    DMCS_PUBLISH = "dmcs_publish"; 
    DMCS_CONSUME = "dmcs_consume"; 
}

void OCS_Bridge::setup_publisher() { 
    try { 
	object pyimport = import("SimplePublisher"); 
	dmcs_publisher = pyimport.attr("SimplePublisher")(this->base_broker_addr); 
    } 
    catch (error_already_set const &) {
	PyErr_Print(); 
    }
} 

void OCS_Bridge::setup_rabbit_consumer() {
    try {
	pthread_t thread1; 
	object pyimport = import("Consumer"); 
	dmcs_consumer = pyimport.attr("Consumer")(this->base_broker_addr, this->DMCS_CONSUME); 
	pthread_create(&thread1, NULL, run_dmcs_consumer, (void *)this); 
    }
    catch (error_already_set const &) {
	PyErr_Print(); 
    } 
    pthread_exit(NULL); 
}

void *run_dmcs_consumer(void *ocs) {
    object pymethod = make_function(OCS_Bridge::on_dmcs_message); 
    ((OCS_Bridge*)ocs)->dmcs_consumer.attr("run")(pymethod); 
    pthread_exit(NULL);
} 

void on_dmcs_message(object ch, object method, object properties, string body) {
    string rabbit_msg = body;      
}

void OCS_Bridge::setup_ocs_consumer() { 
    pthread_t ocsthread; 
    pthread_create(&ocsthread, NULL, run_ocs_consumer, (void *)this); 
    pthread_exit(NULL); 
} 

void OCS_Bridge::run() { 
    Py_Initialize(); 
    this->setup_publisher(); 
    this->setup_rabbit_consumer(); 
    this->setup_ocs_consumer(); 
}

void *run_ocs_consumer(void *ocs) {
    os_time delay_2ms = { 0, 2000000 };
    os_time delay_200ms = { 0, 200000000 };
    dm_logeventC SALInstance;

    #ifdef SAL_SUBSYSTEM_ID_IS_KEYED
	int dmID = 1;
	SAL_dm mgr = SAL_dm(dmID);
    #else
	SAL_dm mgr = SAL_dm();
    #endif

    bool closed = false;
    ReturnCode_t status =  - 1;
    int count = 0;
    while (!closed && count < 1500) { // We dont want the example to run indefinitely
	status = mgr.getEventC(&SALInstance);
	if (status == SAL__OK) {
	    string ocs_msg = SALInstance.message; 
	    try { 
		((OCS_Bridge *)ocs)->dmcs_publisher.attr("publish_message")(((OCS_Bridge *)ocs)->DMCS_PUBLISH, ocs_msg); 
	    }
	    catch (error_already_set const &) {
		PyErr_Print();
	    }
	}
	os_nanoSleep(delay_200ms);
	++count;
    }

    os_nanoSleep(delay_2ms);
    mgr.salShutdown();
    pthread_exit(NULL); 
} 
