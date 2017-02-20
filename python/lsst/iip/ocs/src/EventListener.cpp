#include <iostream> 
#include <sstream> 
#include <string.h> 
#include "OCS_Bridge.h" 
#include "EventListener.h"

using namespace std;
using namespace DDS; 
using namespace dm; 
using namespace AmqpClient;

/* function pointer for EventListener */ 
typedef void (EventListener::*funcptr)(string);

/* map of string name and callback function pointers to use in mapping out message_types to functions */ 
map<string, funcptr> action_handler = {
    {"READOUT", &EventListener::log_readout}, 
    {"START_INTEGRATION", &EventListener::log_start_integration}, 
    {"NEXT_VISIT", &EventListener::log_next_visit}
}; 

/* 
    EventListener listens to event commands such as next_visit, start_integration commands from SAL.
    It extends OCS_Bridge which handles Config file opening and setting up Rabbit publisher.
*/ 
EventListener::EventListener() : OCS_Bridge() { 
    mgr = SAL_dm(); 

    command_args = new ocs_thread_args; 
    command_args->dmgr = mgr; 
    command_args->ocsAmqp = ocs_publisher;
    command_args->q = OCS_PUBLISH;  
} 

/* destructor for EventListener */
EventListener::~EventListener(){ 
}

/* 
    run method is called whenever Event Listener runs. It handles messages by chopping off string
    sent by OCS and calls action handler to publish messages.
    TODO: chopping off things isn't robust
*/
void EventListener::run() { 
    os_time delay_2ms = {0, 2000000}; 
    os_time delay_200ms = {0, 200000000}; 
    dm_logeventC SALInstance; 

    SAL_dm mgr = SAL_dm(); 
    cout << "===========> EVENT LOG Ready <============" << endl; 
    bool closed = false; 
    ReturnCode_t status = -1; 
    while (!closed) { 
	status = mgr.getEventC(&SALInstance); 
	if (status == SAL__OK) { 
	    string msg = SALInstance.message; 
	    int firstcolon = msg.find(":", 0); 
	    int firstcomma = msg.find(",", 0); 
	    string msg_type = msg.substr(firstcolon+2, firstcomma-firstcolon-2); 
	    if (action_handler.count(msg_type) == 1) { 
		funcptr action = action_handler[msg_type]; 
		(this->*action)(msg); 
	    } 
	    else { 
		cout << "MSG_TYPE does not exist." << endl; 
	    } 
	} 
	os_nanoSleep(delay_200ms); 
    } 
    os_nanoSleep(delay_2ms); 
    mgr.salShutdown(); 
} 

/* 
    handles readout message type and publishes to OCS_PUBLISH queue
    :param message: message string which looks like a python dictionary '{"MSG_TYPE": ... }'
*/
void EventListener::log_readout(string message) { 
    cout << "### Event READOUT Ready ..." << endl; 
    ocs_publisher.publish_message(OCS_PUBLISH, message); 
} 

/* 
    handles next_visit message type and publishes to OCS_PUBLISH queue
    :param message: message string which looks like a python dictionary '{"MSG_TYPE": ... }'
*/
void EventListener::log_next_visit(string message) { 
    cout << "### Event NEXTVISIT Ready ..." << endl; 
    ocs_publisher.publish_message(OCS_PUBLISH, message); 
} 

/* 
    handles start_integration message type and publishes to OCS_PUBLISH queue
    :param message: message string which looks like a python dictionary '{"MSG_TYPE": ... }'
*/
void EventListener::log_start_integration(string message) { 
    cout << "### Event START_INTEGRATION Ready ..." << endl; 
    ocs_publisher.publish_message(OCS_PUBLISH, message); 
}

int main() { 
    EventListener cmd; 
    cmd.run(); 
    return 0;
} 
