#include <iostream> 
#include <sstream> 
#include <string.h> 
#include <yaml-cpp/yaml.h>
#include "SAL_dm.h"
#include "OCS_Bridge.h" 
#include "EventListener.h"

using namespace std;
using namespace YAML; 

/* function pointer for EventListener */ 
typedef void (EventListener::*funcptr)(string);

/* map of string name and callback function pointers to use in mapping out message_types to functions */ 
map<string, funcptr> action_handler = {
    {"READOUT", &EventListener::log_readout}, 
    {"START_INTEGRATION", &EventListener::log_start_integration}, 
    {"NEXT_VISIT", &EventListener::log_next_visit}
}; 

EventListener::EventListener() : OCS_Bridge() { 
    mgr = SAL_dm(); 

    command_args = new ocs_thread_args; 
    command_args->dmgr = mgr; 
    command_args->publisher = ocs_publisher;
    command_args->q = OCS_PUBLISH;  
} 

EventListener::~EventListener(){ 
    delete command_args; 
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
            Node node = Load(msg); 
            string msg_type = node["MSG_TYPE"].as<string>(); 
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
    ocs_publisher->publish_message(OCS_PUBLISH, message); 
} 

void EventListener::log_next_visit(string message) { 
    cout << "### Event NEXTVISIT Ready ..." << endl; 
    ocs_publisher->publish_message(OCS_PUBLISH, message); 
} 

void EventListener::log_start_integration(string message) { 
    cout << "### Event START_INTEGRATION Ready ..." << endl; 
    ocs_publisher->publish_message(OCS_PUBLISH, message); 
}

int main() { 
    EventListener cmd; 
    cmd.run(); 
    return 0;
} 
