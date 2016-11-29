#include <pthread.h>
#include <stdio.h> 
#include <string.h>
#include <iostream>
#include "OCS_Bridge.h"
#include <SimpleAmqpClient/SimpleAmqpClient.h>

using namespace DDS;
using namespace dm;
using namespace std; 
using namespace boost::python;
using namespace AmqpClient; 

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

    setup_rabbit_consumer(); 
    setup_publisher(); 

    ocs_consume_args = new thread_args; 
    ocs_consume_args->amqpObj = ocs_publisher; 
    ocs_consume_args->queue_name = OCS_PUBLISH; 
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

void OCS_Bridge::process_ocs_message(Channel::ptr_t publisher, string queue, string message) { 
    BasicMessage::ptr_t msg = BasicMessage::Create(message); 
    publisher->BasicPublish("", queue, msg, true, false); 
}

