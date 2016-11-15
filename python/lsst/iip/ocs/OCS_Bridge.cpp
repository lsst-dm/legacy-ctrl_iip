#include <pthread.h>
#include <stdio.h> 
#include <string.h>
#include <sstream>
#include <iostream>
#include <map>
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

struct thread_args { 
    object pyObj; 
    string broker_addr; 
    string queue_name; 
}; 

OCS_Bridge::OCS_Bridge(string base_addr) { 
    base_broker_addr = base_addr; 
    DMCS_PUBLISH = "dmcs_publish"; 
    DMCS_CONSUME = "dmcs_consume"; 
    Py_Initialize(); 
    setup_publisher(); 
    setup_rabbit_consumer(); 
    setup_ocs_consumer(); 
}

void OCS_Bridge::setup_publisher() { 
    try { 
	object pyimport = import("SimplePublisher"); 
	dmcs_publisher = pyimport.attr("SimplePublisher")(base_broker_addr); 
    } 
    catch (error_already_set const &) {
	PyErr_Print(); 
    }
} 

void OCS_Bridge::setup_rabbit_consumer() {
    try {
	pthread_t thread1; 
	struct thread_args p1; 
	p1.broker_addr = this->base_broker_addr; 
	p1.queue_name = this->DMCS_CONSUME; 
	pthread_create(&thread1, NULL, &OCS_Bridge::run_dmcs_consumer, &p1); 
    }
    catch (error_already_set const &) {
	PyErr_Print(); 
    } 
    pthread_exit(NULL); 
}

void *OCS_Bridge::run_dmcs_consumer(void *params) {
    try { 
        thread_args p = *((thread_args *)params);
	string a = p.broker_addr; 
	string b = p.queue_name;  	
	object pyimport = import("Consumer"); 
	object dmcs = pyimport.attr("Consumer")(a, b); 
	object pymethod = make_function(OCS_Bridge::on_dmcs_message); 
	dmcs.attr("run")(pymethod); 
    } 
    catch(error_already_set const &) { 
	PyErr_Print(); 
    }
    return 0;
} 

void OCS_Bridge::on_dmcs_message(object ch, object method, object properties, dict body) {
    try { 
	int l = len(body); 
	list keys = body.keys(); 
	for (int i = 0; i < l; i++) { 
	    string key = extract<string>(keys[i]); 
	    string value = extract<string>(body[keys[i]]); 
	    cout << key << " " << value << endl;
	} 
    } 
    catch (error_already_set const &) { 
	PyErr_Print(); 
    } 
}

void OCS_Bridge::setup_ocs_consumer() { 
    thread_args pargs; 
    pargs.pyObj = dmcs_publisher; 
    pargs.broker_addr = base_broker_addr; 
    pargs.queue_name = DMCS_PUBLISH; 
    pthread_t ocsthread; 
    pthread_create(&ocsthread, NULL, run_ocs_consumer, &pargs); 
    pthread_exit(NULL); 
} 

void *OCS_Bridge::run_ocs_consumer(void *pargs) {
    thread_args params = *((thread_args *)pargs); 
    object publisher = params.pyObj; 
    string addr = params.broker_addr; 
    string queue = params.queue_name; 
    
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
		cout << ocs_msg << endl; 
		publisher.attr("publish_message")(queue, ocs_msg); 
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
