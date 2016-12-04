#include <iostream> 
#include <sstream> 
#include <string.h> 
#include <pthread.h>
#include <boost/python.hpp>
#include <SimpleAmqpClient/SimpleAmqpClient.h>
#include "OCS_Bridge.h" 
#include "EventListener.h"

using namespace std;
using namespace DDS; 
using namespace dm; 
using namespace AmqpClient;
using namespace boost::python;

extern "C" { 
    OS_API_EXPORT
    int dm_command_controller(); 
} 

class G { 
    public: 
	inline G() { thread_state = PyEval_SaveThread(); }
	inline ~G() { PyEval_RestoreThread(thread_state); thread_state = NULL; }
    private: 
	PyThreadState *thread_state; 
}; 

EventListener::EventListener(string CommandEntity) : OCS_Bridge(CommandEntity) { 
    mgr = SAL_dm(); 
    Py_Initialize();

    cmdEntity = CommandEntity; 
    command_args = new ocs_thread_args; 
    command_args->dmgr = mgr; 
    command_args->ocsAmqp = ocs_publisher;
    command_args->q = OCS_PUBLISH;  
    setup_ocs_consumer();
} 

EventListener::~EventListener(){ 
}

void EventListener::setup_ocs_consumer() { 
    cout << "Setting up OCS COMMAND consumer" << endl; 
    pthread_create(&publishT, NULL, &EventListener::run_event_publish, command_args); 
    pthread_create(&archiveT, NULL, &EventListener::run_event_archive, command_args); 
    //pthread_create(&baseT, NULL, &EventListener::run_event_base, command_args); 
} 


void *EventListener::run_event_publish(void *event_args) { 
    ocs_thread_args *params = ((ocs_thread_args *)event_args);
    SAL_dm mgr = params->dmgr; 
    Channel::ptr_t publisher = params->ocsAmqp; 
    string queue = params->q; 
    
    int cmdId = -1; 
    os_time delay_10ms = {0, 10000000};
 
    dm_logevent_dmPublishedC SALInstance; 
    mgr.salEvent("dm_logevent_dmPublished");
    while (1) { 
	cmdId = mgr.getEvent_dmPublished(&SALInstance); 
	if (cmdId == SAL__OK) { 
	    cout << "=== PUBLISH EVENT received" << endl; 
	    cout << "priority: " << SALInstance.priority << endl; 
	    cout << "visit_identifiers: " << SALInstance.visit_identifier << endl; 
	    cout << "alert_count: " << SALInstance.alert_count << endl; 
	} 	
	os_nanoSleep(delay_10ms); 
    } 
    mgr.salShutdown(); 
    return 0; 
} 

void *EventListener::run_event_archive(void *event_args) { 
    ocs_thread_args *params = ((ocs_thread_args *)event_args);
    SAL_dm mgr = params->dmgr; 
    Channel::ptr_t publisher = params->ocsAmqp; 
    string queue = params->q; 
    
    int cmdId = -1; 
    os_time delay_10ms = {0, 10000000};
 
    dm_logevent_dmToArchiveC SALInstance; 
    mgr.salEvent("dm_logevent_dmToArchive");
    while (1) { 
	cmdId = mgr.getEvent_dmToArchive(&SALInstance); 
	if (cmdId == SAL__OK) { 
	    cout << "=== TOARCHIVE EVENT received." << endl;
	    cout << "priority: " << SALInstance.priority << endl; 
	    cout << "image_id: " << SALInstance.image_id << endl;
	} 	
	os_nanoSleep(delay_10ms); 
    } 
    mgr.salShutdown(); 
    return 0; 
} 

void *EventListener::run_event_base(void *event_args) { 
    ocs_thread_args *params = ((ocs_thread_args *)event_args);
    SAL_dm mgr = params->dmgr; 
    Channel::ptr_t publisher = params->ocsAmqp; 
    string queue = params->q; 
    
    int cmdId = -1; 
    os_time delay_10ms = {0, 10000000};
 
    dm_logevent_dmToBaseC SALInstance;
    mgr.salEvent("dm_logevent_dmToBase");
    while (1) { 
	cmdId = mgr.getEvent_dmToBase(&SALInstance); 
	if (cmdId == SAL__OK) { 
	    cout << "=== TOBASE EVENT received." << endl; 
	    cout << "priority: " << SALInstance.priority << endl; 
	    cout << "image_id: " << SALInstance.image_id << endl;
	} 	
	os_nanoSleep(delay_10ms); 
    } 
    mgr.salShutdown(); 
    return 0; 
} 

int main() { 
    EventListener cmd("PromptProcessor"); 
    pthread_exit(NULL); 
    return 0;
} 
