#include <iostream> 
#include <sstream> 
#include <string.h> 
#include <pthread.h>
#include <SimpleAmqpClient/SimpleAmqpClient.h>
#include "OCS_Bridge.h" 
#include "CommandListener.h"

using namespace std;
using namespace DDS; 
using namespace dm; 
using namespace AmqpClient;

CommandListener::CommandListener(string CommandEntity) : OCS_Bridge(CommandEntity) { 
    mgr = SAL_dm(); 

    cmdEntity = CommandEntity; 
    command_args = new ocs_thread_args; 
    command_args->dmgr = mgr; 
    command_args->ocsAmqp = ocs_publisher;
    command_args->q = OCS_PUBLISH;  
    command_args->entity = cmdEntity; 
    setup_ocs_consumer();
} 

CommandListener::~CommandListener(){ 
}

void CommandListener::setup_ocs_consumer() { 
    cout << "Setting up OCS COMMAND consumer" << endl; 
    pthread_create(&ocsthread, NULL, &CommandListener::run_ocs_consumer, command_args); 
} 

void *CommandListener::run_ocs_consumer(void *pargs) { 
    ocs_thread_args *params = ((ocs_thread_args *)pargs); 
    SAL_dm mgr = params->dmgr; 
    Channel::ptr_t publisher = params->ocsAmqp; 
    string queue = params->q; 
    string command_entity = params->entity; 
    
    os_time delay_10ms = {0, 10000000}; 

    int timeout = 1; 
    int cmdId = -1;

    mgr.salProcessor("dm_command_start"); 
    mgr.salProcessor("dm_command_stop");
    mgr.salProcessor("dm_command_enable");
    mgr.salProcessor("dm_command_disable");
    mgr.salProcessor("dm_command_enterControl");
    mgr.salProcessor("dm_command_standby");
    mgr.salProcessor("dm_command_exitControl");
    mgr.salProcessor("dm_command_abort");
    
    cout << "=== dm COMMAND controller ready" << endl; 

    while (1) { 
	dm_start(cmdId, timeout, delay_10ms, publisher, queue, command_entity, mgr); 
	dm_stop(cmdId, timeout, delay_10ms, publisher, queue, command_entity, mgr);  
	dm_enable(cmdId, timeout, delay_10ms, publisher, queue, command_entity, mgr);  
	dm_disable(cmdId, timeout, delay_10ms, publisher, queue, command_entity, mgr);  
	dm_enterControl(cmdId, timeout, delay_10ms, publisher, queue, command_entity, mgr);  
	dm_standby(cmdId, timeout, delay_10ms, publisher, queue, command_entity, mgr);  
	dm_exitControl(cmdId, timeout, delay_10ms, publisher, queue, command_entity, mgr);  
	dm_abort(cmdId, timeout, delay_10ms, publisher, queue, command_entity, mgr);  
    }
    mgr.salShutdown(); 
    return 0;
}  

void CommandListener::dm_start(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, string cmdEntity, SAL_dm mgr) { 
    dm_command_startC SALInstance; 
    
    cmdId = mgr.acceptCommand_start(&SALInstance); 
    
    if (cmdId > 0 && cmdEntity == SALInstance.device) { 
	cout << "== START Command " << endl;
	cout << "configuration: " << SALInstance.configuration << endl; 
	ostringstream message; 
	message << "{MSG_TYPE: START, STATE: " << SALInstance.configuration << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_stop(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, string cmdEntity, SAL_dm mgr) { 
    dm_command_stopC SALInstance; 
    
    cmdId = mgr.acceptCommand_stop(&SALInstance); 
    
    if (cmdId > 0 && cmdEntity == SALInstance.device) { 
	cout << "== STOP Command " << endl;
	cout << "state: " << SALInstance.state << endl; 
	ostringstream message; 
	message << "{MSG_TYPE: STOP, STATE: " << SALInstance.state << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_enable(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, string cmdEntity, SAL_dm mgr) { 
    dm_command_enableC SALInstance; 
    
    cmdId = mgr.acceptCommand_enable(&SALInstance); 
    
    if (cmdId > 0 && cmdEntity == SALInstance.device) { 
	cout << "== ENABLE Command " << endl;
	cout << "state: " << SALInstance.state << endl; 
	ostringstream message; 
	message << "{MSG_TYPE: ENABLE, STATE: " << SALInstance.state << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_disable(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, string cmdEntity, SAL_dm mgr) { 
    dm_command_disableC SALInstance; 
    
    cmdId = mgr.acceptCommand_disable(&SALInstance); 
    
    if (cmdId > 0 && cmdEntity == SALInstance.device) { 
	cout << "== DISABLE Command " << endl;
	cout << "state: " << SALInstance.state << endl; 
	ostringstream message; 
	message << "{MSG_TYPE: DISABLE, STATE: " << SALInstance.state << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_enterControl(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, string cmdEntity, SAL_dm mgr) { 
    dm_command_enterControlC SALInstance; 
    
    cmdId = mgr.acceptCommand_enterControl(&SALInstance); 
    
    if (cmdId > 0 && cmdEntity == SALInstance.device) { 
	cout << "== ENTERCONTROL Command " << endl;
	cout << "state: " << SALInstance.state << endl; 
	ostringstream message; 
	message << "{MSG_TYPE: ENTERCONTROL, STATE: " << SALInstance.state << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_standby(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, string cmdEntity, SAL_dm mgr) { 
    dm_command_standbyC SALInstance; 
    
    cmdId = mgr.acceptCommand_standby(&SALInstance); 
    
    if (cmdId > 0 && cmdEntity == SALInstance.device) { 
	cout << "== STANDBY Command " << endl;
	cout << "state: " << SALInstance.state << endl; 
	ostringstream message; 
	message << "{MSG_TYPE: STANDBY, STATE: " << SALInstance.state << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_exitControl(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, string cmdEntity, SAL_dm mgr) { 
    dm_command_exitControlC SALInstance; 
    
    cmdId = mgr.acceptCommand_exitControl(&SALInstance); 
    
    if (cmdId > 0 && cmdEntity == SALInstance.device) { 
	cout << "== EXITCONTROL Command " << endl;
	cout << "state: " << SALInstance.state << endl; 
	ostringstream message; 
	message << "{MSG_TYPE: EXITCONTROL, STATE: " << SALInstance.state << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_abort(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, string cmdEntity, SAL_dm mgr) { 
    dm_command_abortC SALInstance; 
    
    cmdId = mgr.acceptCommand_abort(&SALInstance); 
    
    if (cmdId > 0 && cmdEntity == SALInstance.device) { 
	cout << "== ABORT Command " << endl;
	cout << "state: " << SALInstance.state << endl; 
	ostringstream message; 
	message << "{MSG_TYPE: ABORT, STATE: " << SALInstance.state << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
}
 
int main() { 
    CommandListener cmd("PromptProcessor"); 
    pthread_exit(NULL); 
    return 0;
} 
