#include <iostream> 
#include <sstream> 
#include <pthread.h>
#include <SimpleAmqpClient/SimpleAmqpClient.h>
#include "OCS_Bridge.h" 
#include "CommandListener.h"
#include <string>

using namespace std;
using namespace DDS; 
using namespace dm; 
using namespace AmqpClient;

CommandListener::CommandListener() : OCS_Bridge() { 
    mgr = SAL_dm(); 

    command_args = new ocs_thread_args; 
    command_args->dmgr = mgr; 
    command_args->ocsAmqp = ocs_publisher;
    command_args->q = OCS_PUBLISH;  
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
	dm_start(cmdId, timeout, delay_10ms, publisher, queue, mgr); 
	dm_stop(cmdId, timeout, delay_10ms, publisher, queue, mgr);  
	dm_enable(cmdId, timeout, delay_10ms, publisher, queue, mgr);  
	dm_disable(cmdId, timeout, delay_10ms, publisher, queue, mgr);  
	dm_enterControl(cmdId, timeout, delay_10ms, publisher, queue, mgr);  
	dm_standby(cmdId, timeout, delay_10ms, publisher, queue, mgr);  
	dm_exitControl(cmdId, timeout, delay_10ms, publisher, queue, mgr);  
	dm_abort(cmdId, timeout, delay_10ms, publisher, queue, mgr);  
    }
    mgr.salShutdown(); 
    return 0;
}  

void CommandListener::dm_start(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, SAL_dm mgr) { 
    dm_command_startC SALInstance; 
    
    cmdId = mgr.acceptCommand_start(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== START Command " << endl;
	ostringstream message; 
	message << "{MSG_TYPE: START, DEVICE: " << SALInstance.device << ", CMD_ID: " << to_string(cmdId) << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_stop(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, SAL_dm mgr) { 
    dm_command_stopC SALInstance; 
    
    cmdId = mgr.acceptCommand_stop(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== STOP Command " << endl;
	ostringstream message; 
	message << "{MSG_TYPE: STOP, DEVICE: " << SALInstance.device << ", CMD_ID: " << to_string(cmdId) << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_enable(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, SAL_dm mgr) { 
    dm_command_enableC SALInstance; 
    
    cmdId = mgr.acceptCommand_enable(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ENABLE Command " << endl;
	ostringstream message; 
	message << "{MSG_TYPE: ENABLE, DEVICE: " << SALInstance.device << ", CMD_ID: " << to_string(cmdId) << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_disable(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, SAL_dm mgr) { 
    dm_command_disableC SALInstance; 
    
    cmdId = mgr.acceptCommand_disable(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== DISABLE Command " << endl;
	ostringstream message; 
	message << "{MSG_TYPE: DISABLE, DEVICE: " << SALInstance.device << ", CMD_ID: " << to_string(cmdId) << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_enterControl(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, SAL_dm mgr) { 
    dm_command_enterControlC SALInstance; 
    
    cmdId = mgr.acceptCommand_enterControl(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ENTERCONTROL Command " << endl;
	ostringstream message; 
	message << "{MSG_TYPE: ENTERCONTROL, DEVICE: " << SALInstance.device << ", CMD_ID: " << to_string(cmdId) << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_standby(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, SAL_dm mgr) { 
    dm_command_standbyC SALInstance; 
    
    cmdId = mgr.acceptCommand_standby(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== STANDBY Command " << endl;
	ostringstream message; 
	message << "{MSG_TYPE: STANDBY, DEVICE: " << SALInstance.device << ", CMD_ID: " << to_string(cmdId) << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_exitControl(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, SAL_dm mgr) { 
    dm_command_exitControlC SALInstance; 
    
    cmdId = mgr.acceptCommand_exitControl(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== OFFLINE Command " << endl;
	ostringstream message; 
	message << "{MSG_TYPE: OFFLINE, DEVICE: " << SALInstance.device << ", CMD_ID: " << to_string(cmdId) << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::dm_abort(int cmdId, int timeout, os_time delay_10ms, Channel::ptr_t publisher, string queue, SAL_dm mgr) { 
    dm_command_abortC SALInstance; 
    
    cmdId = mgr.acceptCommand_abort(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== FAULT Command " << endl;
	ostringstream message; 
	message << "{MSG_TYPE: FAULT, DEVICE: " << SALInstance.device << ", CMD_ID: " << to_string(cmdId) << "}"; 
	OCS_Bridge::process_ocs_message(publisher, queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
}

int main() { 
    CommandListener cmd; 
    pthread_exit(NULL); 
    return 0; 
} 
