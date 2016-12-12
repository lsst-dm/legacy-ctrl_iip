#include <iostream> 
#include <sstream> 
#include <string.h> 
#include "OCS_Bridge.h" 
#include "EventListener.h"

using namespace std;
using namespace DDS; 
using namespace dm; 
using namespace AmqpClient;

typedef void (EventListener::*funcptr)(string); 
map<string, funcptr> action_handler = {
    {"READOUT", &EventListener::log_readout}, 
    {"START_INTEGRATION", &EventListener::log_start_integration}, 
    {"NEXT_VISIT", &EventListener::log_next_visit}
}; 

EventListener::EventListener() : OCS_Bridge() { 
    mgr = SAL_dm(); 

    command_args = new ocs_thread_args; 
    command_args->dmgr = mgr; 
    command_args->ocsAmqp = ocs_publisher;
    command_args->q = OCS_PUBLISH;  
} 

EventListener::~EventListener(){ 
}


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

void EventListener::log_readout(string message) { 
    cout << "### Event READOUT Ready ..." << endl; 
    process_ocs_message(ocs_publisher, OCS_PUBLISH, message);  
} 

void EventListener::log_next_visit(string message) { 
    cout << "### Event NEXTVISIT Ready ..." << endl; 
    process_ocs_message(ocs_publisher, OCS_PUBLISH, message);  
} 

void EventListener::log_start_integration(string message) { 
    cout << "### Event START_INTEGRATION Ready ..." << endl; 
    process_ocs_message(ocs_publisher, OCS_PUBLISH, message);  
}

int main() { 
    EventListener cmd; 
    cmd.run(); 
    return 0;
} 
