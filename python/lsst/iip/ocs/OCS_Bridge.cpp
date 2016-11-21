#include <pthread.h>
#include <stdio.h> 
#include <string.h>
#include <iostream>
#include <map>
#include "OCS_Bridge.h"
#include <SimpleAmqpClient/SimpleAmqpClient.h>

using namespace DDS;
using namespace dm;
using namespace std; 
using namespace boost::python;
using namespace AmqpClient; 

/* entry point exported and demangled so symbol can be found in shared library */
extern "C" { 
    OS_API_EXPORT
    void *run_ocs_consumer(void *);
}


OCS_Bridge::OCS_Bridge(string base_addr) { 
    base_broker_addr = base_addr; 
    OCS_PUBLISH = "ocs_publish"; 
    OCS_CONSUME = "ocs_consume"; 
    Py_Initialize(); 
    cout << "RUNNING THREADS >>>> " << endl; 

    object pyimport = import("Consumer"); 
    ocs_consumer = pyimport.attr("Consumer")(base_broker_addr, OCS_CONSUME); 
    object pymethod = make_function(OCS_Bridge::on_dmcs_message); 

    rabbit_consume_args = new thread_args; 
    rabbit_consume_args->pyObj = ocs_consumer; 
    rabbit_consume_args->func = pymethod; 
    
    ocs_consume_args = new thread_args; 
    ocs_consume_args->amqpObj = ocs_publisher; 
    ocs_consume_args->broker_addr = base_broker_addr; 
    ocs_consume_args->queue_name = OCS_PUBLISH; 

    setup_rabbit_consumer(); 
    setup_publisher(); 
    setup_ocs_consumer(); 
}

OCS_Bridge::~OCS_Bridge() {
    delete(ocs_consume_args); 
    delete(rabbit_consume_args); 
} 

void OCS_Bridge::setup_publisher() { 
    cout << "Setting up RABBIT publisher" << endl; 
    ocs_publisher =  Channel::CreateFromUri(base_broker_addr); 
} 

void OCS_Bridge::setup_rabbit_consumer() {
    cout << "Setting up RABBIT consumer" << endl; 
    pthread_create(&consume_thread, NULL, &OCS_Bridge::run_dmcs_consumer, rabbit_consume_args); 
}

void *OCS_Bridge::run_dmcs_consumer(void *params) {
    try { 
        thread_args *p = ((thread_args *)params);
	object consumer = p->pyObj; 
	object callback = p->func; 
	consumer.attr("run")(callback); 
    } 
    catch(error_already_set const &) { 
	PyErr_Print(); 
    }
    return 0;
} 

void OCS_Bridge::on_dmcs_message(object ch, object method, object properties, dict body) {
    try { 
	cout << "###########  RECEIVING MESSAGE ############" << endl; 
	int l = len(body); 
	list keys = body.keys(); 
	for (int i = 0; i < l; i++) { 
	    string key = extract<string>(keys[i]); 
	    string value = extract<string>(body[keys[i]]); 
	    cout << key + ": " + value << endl; 
	} 
    } 
    catch (error_already_set const &) { 
	PyErr_Print(); 
    } 
}

void OCS_Bridge::setup_ocs_consumer() { 
    cout << "Setting up OCS consumer" << endl; 
    pthread_create(&ocsthread, NULL, run_ocs_consumer, ocs_consume_args); 
} 

void OCS_Bridge::process_ocs_message(Channel::ptr_t publisher, string queue, string message) { 
    cout << "INSIDE PROCESS_OCS" << endl; 
    BasicMessage::ptr_t msg = BasicMessage::Create(message); 
    publisher->BasicPublish("", queue, msg, true, false); 
}

void *OCS_Bridge::run_ocs_consumer(void *pargs) {
    cout << "INSIDE RUN_OCS" << endl; 
    thread_args *params = ((thread_args *)pargs); 
    Channel::ptr_t publisher = params->amqpObj; 
    string addr = params->broker_addr; 
    string queue = params->queue_name; 
    
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
		process_ocs_message(publisher, queue, ocs_msg); 
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
    return 0;
} 

int main() { 
    OCS_Bridge ocs("amqp://ocs:ocs@141.142.208.241/%2fbridge"); 
    pthread_exit(NULL);
    return 0;
} 
