#include "Toolsmod.h"
#include <iostream> 
#include <sstream> 
#include <pthread.h>
#include <string>
#include "SAL_archiver.h" 
#include "SAL_catchuparchiver.h"
#include "SAL_processingcluster.h" 
#include "OCS_Bridge.h" 
#include "CommandListener.h"
#include <unistd.h> 
#include <thread> 
#include <chrono> 

using namespace std;

int next_timed_ack_id = 0; 

CommandListener::CommandListener() : OCS_Bridge() { 
    archiver = SAL_archiver(); 
    catchuparchiver = SAL_catchuparchiver(); 
    processingcluster = SAL_processingcluster(); 

    command_args = new ocs_thread_args; 
    command_args->archie = archiver; 
    command_args->catchuparchie = catchuparchiver; 
    command_args->processie = processingcluster; 
    command_args->publisher = ocs_publisher;
    command_args->queue = OCS_PUBLISH;  

    setup_ocs_consumer();
    setup_resolve_publisher(); 
} 

CommandListener::~CommandListener(){ 
}

void CommandListener::setup_ocs_consumer() { 
    cout << "Setting up OCS COMMAND consumer" << endl; 
    pthread_create(&ocsthread, NULL, &CommandListener::run_ocs_consumer, command_args); 
} 

void CommandListener::setup_resolve_publisher() { 
    cout << "Setting up OCS RESOLVE publisher" << endl; 
    pthread_create(&resolvethread, NULL, &CommandListener::run_resolve_publisher, command_args); 
} 

void *CommandListener::run_resolve_publisher(void *pargs) { 
    usleep(10000000); 
    ocs_thread_args *params = ((ocs_thread_args *)pargs); 
    SimplePublisher *rabbit_publisher = params->publisher; 
    while (1) { 
	rabbit_publisher->publish_message("DMCS_OCS_PUBLISH", "{MSG_TYPE: RESOLVE_ACK}"); 
	usleep(3000000);
    }  
} 

void *CommandListener::run_ocs_consumer(void *pargs) { 
    ocs_thread_args *params = ((ocs_thread_args *)pargs); 
    SAL_archiver archiver = params->archie; 
    SAL_catchuparchiver catchuparchiver = params->catchuparchie; 
    SAL_processingcluster processingcluster = params->processie; 
    SimplePublisher* rabbit_publisher = params->publisher; 
    string queue = params->queue; 
    
    os_time delay_10ms = {0, 10000000}; 

    int timeout = 1; 
    int cmdId = -1;

    archiver.salProcessor("archiver_command_start"); 
    archiver.salProcessor("archiver_command_stop"); 
    archiver.salProcessor("archiver_command_enable"); 
    archiver.salProcessor("archiver_command_disable"); 
    archiver.salProcessor("archiver_command_standby"); 
    archiver.salProcessor("archiver_command_abort"); 
    archiver.salProcessor("archiver_command_enterControl"); 
    archiver.salProcessor("archiver_command_exitControl"); 

    
    catchuparchiver.salProcessor("catchuparchiver_command_start"); 
    catchuparchiver.salProcessor("catchuparchiver_command_stop"); 
    catchuparchiver.salProcessor("catchuparchiver_command_enable"); 
    catchuparchiver.salProcessor("catchuparchiver_command_disable"); 
    catchuparchiver.salProcessor("catchuparchiver_command_standby"); 
    catchuparchiver.salProcessor("catchuparchiver_command_abort"); 
    catchuparchiver.salProcessor("catchuparchiver_command_enterControl"); 
    catchuparchiver.salProcessor("catchuparchiver_command_exitControl"); 


    processingcluster.salProcessor("processingcluster_command_start"); 
    processingcluster.salProcessor("processingcluster_command_stop"); 
    processingcluster.salProcessor("processingcluster_command_enable"); 
    processingcluster.salProcessor("processingcluster_command_disable"); 
    processingcluster.salProcessor("processingcluster_command_standby"); 
    processingcluster.salProcessor("processingcluster_command_abort"); 
    processingcluster.salProcessor("processingcluster_command_enterControl"); 
    processingcluster.salProcessor("processingcluster_command_exitControl"); 
    
    cout << "=== dm COMMAND controller ready" << endl; 

    while (1) { 
	archiver_start(cmdId, timeout, delay_10ms, rabbit_publisher, queue, archiver); 
	archiver_stop(cmdId, timeout, delay_10ms, rabbit_publisher, queue, archiver); 
	archiver_enable(cmdId, timeout, delay_10ms, rabbit_publisher, queue, archiver); 
	archiver_disable(cmdId, timeout, delay_10ms, rabbit_publisher, queue, archiver); 
	archiver_standby(cmdId, timeout, delay_10ms, rabbit_publisher, queue, archiver); 
	archiver_abort(cmdId, timeout, delay_10ms, rabbit_publisher, queue, archiver); 
	archiver_enterControl(cmdId, timeout, delay_10ms, rabbit_publisher, queue, archiver); 
	archiver_exitControl(cmdId, timeout, delay_10ms, rabbit_publisher, queue, archiver); 

	catchuparchiver_start(cmdId, timeout, delay_10ms, rabbit_publisher, queue, catchuparchiver); 
	catchuparchiver_stop(cmdId, timeout, delay_10ms, rabbit_publisher, queue, catchuparchiver); 
	catchuparchiver_enable(cmdId, timeout, delay_10ms, rabbit_publisher, queue, catchuparchiver); 
	catchuparchiver_disable(cmdId, timeout, delay_10ms, rabbit_publisher, queue, catchuparchiver); 
	catchuparchiver_standby(cmdId, timeout, delay_10ms, rabbit_publisher, queue, catchuparchiver); 
	catchuparchiver_abort(cmdId, timeout, delay_10ms, rabbit_publisher, queue, catchuparchiver); 
	catchuparchiver_enterControl(cmdId, timeout, delay_10ms, rabbit_publisher, queue, catchuparchiver); 
	catchuparchiver_exitControl(cmdId, timeout, delay_10ms, rabbit_publisher, queue, catchuparchiver); 

	processingcluster_start(cmdId, timeout, delay_10ms, rabbit_publisher, queue, processingcluster); 
	processingcluster_stop(cmdId, timeout, delay_10ms, rabbit_publisher, queue, processingcluster); 
	processingcluster_enable(cmdId, timeout, delay_10ms, rabbit_publisher, queue, processingcluster); 
	processingcluster_disable(cmdId, timeout, delay_10ms, rabbit_publisher, queue, processingcluster); 
	processingcluster_standby(cmdId, timeout, delay_10ms, rabbit_publisher, queue, processingcluster); 
	processingcluster_abort(cmdId, timeout, delay_10ms, rabbit_publisher, queue, processingcluster); 
	processingcluster_enterControl(cmdId, timeout, delay_10ms, rabbit_publisher, queue, processingcluster); 
	processingcluster_exitControl(cmdId, timeout, delay_10ms, rabbit_publisher, queue, processingcluster); 
    }
    archiver.salShutdown(); 
    catchuparchiver.salShutdown(); 
    processingcluster.salShutdown();
    return 0;
}  

void CommandListener::archiver_start(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_archiver mgr) { 
    archiver_command_startC SALInstance; 
    
    cmdId = mgr.acceptCommand_start(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ARCHIVER START Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("START"); 
	message << "{MSG_TYPE: START, DEVICE: AR, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "START: " << message.str() << endl; 

	ostringstream message2; 
	message2 << "{MSG_TYPE: BOOK_KEEPING, ACK_ID: " << ack_id << ", ACK_DELAY: 2, CHECKBOX: false, TIME: " << get_current_time() 
		     << ", CMD_ID: " << to_string(cmdId) << "}"; 
	cout << "MSG2: " << message2.str() << endl; 
	publisher->publish_message("DMCS_OCS_PUBLISH", message2.str());  
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 

void CommandListener::archiver_stop(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_archiver mgr) { 
    archiver_command_stopC SALInstance; 
    
    cmdId = mgr.acceptCommand_stop(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ARCHIVER STOP Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("STOP"); 
	message << "{MSG_TYPE: STOP, DEVICE: AR, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "STOP: " << message.str() << endl; 

	ostringstream message2; 
	message2 << "{MSG_TYPE: BOOK_KEEPING, ACK_ID: " << ack_id << ", ACK_DELAY: 2, CHECKBOX: false, TIME: " << get_current_time() 
		     << ", CMD_ID: " << to_string(cmdId) << "}"; 
	cout << "MSG2: " << message2.str() << endl; 
	publisher->publish_message("DMCS_OCS_PUBLISH", message2.str());  
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::archiver_enable(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_archiver mgr) { 
    archiver_command_enableC SALInstance; 
    
    cmdId = mgr.acceptCommand_enable(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ARCHIVER ENABLE Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("ENABLE"); 
	message << "{MSG_TYPE: ENABLE, DEVICE: AR, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "ENABLE: " << message.str() << endl; 
	
	ostringstream message2; 
	message2 << "{MSG_TYPE: BOOK_KEEPING, ACK_ID: " << ack_id << ", ACK_DELAY: 2, CHECKBOX: false, TIME: " << get_current_time() 
		     << ", CMD_ID: " << to_string(cmdId) << "}"; 
	cout << "MSG2: " << message2.str() << endl; 
	publisher->publish_message("DMCS_OCS_PUBLISH", message2.str());  
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::archiver_disable(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_archiver mgr) { 
    archiver_command_disableC SALInstance; 
    
    cmdId = mgr.acceptCommand_disable(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ARCHIVER DISABLE Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("DISABLE"); 
	message << "{MSG_TYPE: DISABLE, DEVICE: AR, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "DISABLE: " << message.str() << endl; 

	ostringstream message2; 
	message2 << "{MSG_TYPE: BOOK_KEEPING, ACK_ID: " << ack_id << ", ACK_DELAY: 2, CHECKBOX: false, TIME: " << get_current_time() 
		     << ", CMD_ID: " << to_string(cmdId) << "}"; 
	cout << "MSG2: " << message2.str() << endl; 
	publisher->publish_message("DMCS_OCS_PUBLISH", message2.str());  
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::archiver_standby(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_archiver mgr) { 
    archiver_command_standbyC SALInstance; 
    
    cmdId = mgr.acceptCommand_standby(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ARCHIVER STANDBY Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("STANDBY"); 
	message << "{MSG_TYPE: STANDBY, DEVICE: AR, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "STANDBY: " << message.str() << endl; 

	ostringstream message2; 
	message2 << "{MSG_TYPE: BOOK_KEEPING, ACK_ID: " << ack_id << ", ACK_DELAY: 2, CHECKBOX: false, TIME: " << get_current_time() 
		     << ", CMD_ID: " << to_string(cmdId) << "}"; 
	cout << "MSG2: " << message2.str() << endl; 
	publisher->publish_message("DMCS_OCS_PUBLISH", message2.str());  
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::archiver_abort(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_archiver mgr) { 
    archiver_command_abortC SALInstance; 
    
    cmdId = mgr.acceptCommand_abort(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ARCHIVER ABORT Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("ABORT"); 
	message << "{MSG_TYPE: FAULT, DEVICE: AR, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "ABORT: " << message.str() << endl; 

	ostringstream message2; 
	message2 << "{MSG_TYPE: BOOK_KEEPING, ACK_ID: " << ack_id << ", ACK_DELAY: 2, CHECKBOX: false, TIME: " << get_current_time() 
		     << ", CMD_ID: " << to_string(cmdId) << "}"; 
	cout << "MSG2: " << message2.str() << endl; 
	publisher->publish_message("DMCS_OCS_PUBLISH", message2.str());  
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::archiver_enterControl(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_archiver mgr) { 
    archiver_command_enterControlC SALInstance; 
    
    cmdId = mgr.acceptCommand_enterControl(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ARCHIVER ENTERCONTROL Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("ENTERCONTROL"); 
	message << "{MSG_TYPE: ENTERCONTROL, DEVICE: AR, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "ENTERCONTROL: " << message.str() << endl; 

	ostringstream message2; 
	message2 << "{MSG_TYPE: BOOK_KEEPING, ACK_ID: " << ack_id << ", ACK_DELAY: 2, CHECKBOX: false, TIME: " << get_current_time() 
		     << ", CMD_ID: " << to_string(cmdId) << "}"; 
	cout << "MSG2: " << message2.str() << endl; 
	publisher->publish_message("DMCS_OCS_PUBLISH", message2.str());  
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::archiver_exitControl(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_archiver mgr) { 
    archiver_command_exitControlC SALInstance; 
    
    cmdId = mgr.acceptCommand_exitControl(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ARCHIVER EXITCONTROL Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("EXITCONTROL"); 
	message << "{MSG_TYPE: OFFLINE, DEVICE: AR, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "OFFLINE: " << message.str() << endl; 

	ostringstream message2; 
	message2 << "{MSG_TYPE: BOOK_KEEPING, ACK_ID: " << ack_id << ", ACK_DELAY: 2, CHECKBOX: false, TIME: " << get_current_time() 
		     << ", CMD_ID: " << to_string(cmdId) << "}"; 
	cout << "MSG2: " << message2.str() << endl; 
	publisher->publish_message("DMCS_OCS_PUBLISH", message2.str());  
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::catchuparchiver_start(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_catchuparchiver mgr) { 
    catchuparchiver_command_startC SALInstance; 
    
    cmdId = mgr.acceptCommand_start(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== CATCHUPARCHIVER START Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("START"); 
	message << "{MSG_TYPE: START, DEVICE: CU, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "START: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::catchuparchiver_stop(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_catchuparchiver mgr) { 
    catchuparchiver_command_stopC SALInstance; 
    
    cmdId = mgr.acceptCommand_stop(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== CATCHUPARCHIVER STOP Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("STOP"); 
	message << "{MSG_TYPE: STOP, DEVICE: CU, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "STOP: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::catchuparchiver_enable(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_catchuparchiver mgr) { 
    catchuparchiver_command_enableC SALInstance; 
    
    cmdId = mgr.acceptCommand_enable(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== CATCHUPARCHIVER ENABLE Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("ENABLE"); 
	message << "{MSG_TYPE: ENABLE, DEVICE: CU, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "ENABLE: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::catchuparchiver_disable(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_catchuparchiver mgr) { 
    catchuparchiver_command_disableC SALInstance; 
    
    cmdId = mgr.acceptCommand_disable(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== CATCHUPARCHIVER DISABLE Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("DISABLE"); 
	message << "{MSG_TYPE: DISABLE, DEVICE: CU, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "DISABLE: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::catchuparchiver_standby(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_catchuparchiver mgr) { 
    catchuparchiver_command_standbyC SALInstance; 
    
    cmdId = mgr.acceptCommand_standby(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== CatchupArchiver STANDBY Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("STANDBY"); 
	message << "{MSG_TYPE: STANDBY, DEVICE: CU, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "STANDBY: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::catchuparchiver_abort(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_catchuparchiver mgr) { 
    catchuparchiver_command_abortC SALInstance; 
    
    cmdId = mgr.acceptCommand_abort(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== CatchupArchiver ABORT Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("ABORT"); 
	message << "{MSG_TYPE: ABORT, DEVICE: CU, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "ABORT: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::catchuparchiver_enterControl(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_catchuparchiver mgr) { 
    catchuparchiver_command_enterControlC SALInstance; 
    
    cmdId = mgr.acceptCommand_enterControl(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== CatchupArchiver ENTERCONTROL Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("ENTERCONTROL"); 
	message << "{MSG_TYPE: ENTERCONTROL, DEVICE: CU, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "ENTERCONTROL: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::catchuparchiver_exitControl(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_catchuparchiver mgr) { 
    catchuparchiver_command_exitControlC SALInstance; 
    
    cmdId = mgr.acceptCommand_exitControl(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== CatchupArchiver EXITCONTROL Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("EXITCONTROL"); 
	message << "{MSG_TYPE: EXITCONTROL, DEVICE: CU, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "EXITCONTROL: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::processingcluster_start(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_processingcluster mgr) { 
    processingcluster_command_startC SALInstance; 
    
    cmdId = mgr.acceptCommand_start(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ProcessingCluster START Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("START"); 
	message << "{MSG_TYPE: START, DEVICE: PP, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "START: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::processingcluster_stop(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_processingcluster mgr) { 
    processingcluster_command_stopC SALInstance; 
    
    cmdId = mgr.acceptCommand_stop(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ProcessingCluster STOP Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("STOP"); 
	message << "{MSG_TYPE: STOP, DEVICE: PP, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "STOP: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::processingcluster_enable(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_processingcluster mgr) { 
    processingcluster_command_enableC SALInstance; 
    
    cmdId = mgr.acceptCommand_enable(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ProcessingCluster ENABLE Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("ENABLE"); 
	message << "{MSG_TYPE: ENABLE, DEVICE: PP, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "ENABLE: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::processingcluster_disable(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_processingcluster mgr) { 
    processingcluster_command_disableC SALInstance; 
    
    cmdId = mgr.acceptCommand_disable(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ProcessingCluster DISABLE Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("ENABLE"); 
	message << "{MSG_TYPE: DISABLE, DEVICE: PP, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "DISABLE: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::processingcluster_standby(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_processingcluster mgr) { 
    processingcluster_command_standbyC SALInstance; 
    
    cmdId = mgr.acceptCommand_standby(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ProcessingCluster STANDBY Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("STANDBY"); 
	message << "{MSG_TYPE: STANDBY, DEVICE: PP, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "STANDBY: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::processingcluster_abort(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_processingcluster mgr) { 
    processingcluster_command_abortC SALInstance; 
    
    cmdId = mgr.acceptCommand_abort(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ProcessingCluster ABORT Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("ABORT"); 
	message << "{MSG_TYPE: ABORT, DEVICE: PP, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "ABORT: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::processingcluster_enterControl(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_processingcluster mgr) { 
    processingcluster_command_enterControlC SALInstance; 
   
    cmdId = mgr.acceptCommand_enterControl(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ProcessingCluster ENTERCONTROL Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("ENTERCONTROL"); 
	message << "{MSG_TYPE: ENTERCONTROL, DEVICE: PP, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "ENTERCONTROL: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
void CommandListener::processingcluster_exitControl(int cmdId, int timeout, os_time delay_10ms, SimplePublisher* publisher, string queue, SAL_processingcluster mgr) { 
    processingcluster_command_exitControlC SALInstance; 
    
    cmdId = mgr.acceptCommand_exitControl(&SALInstance); 
    
    if (cmdId > 0) { 
	cout << "== ProcessingCluster EXITCONTROL Command " << endl;
	ostringstream message; 
	string ack_id = get_next_timed_ack_id("EXITCONTROL"); 
	message << "{MSG_TYPE: EXITCONTROL, DEVICE: PP, CMD_ID: " << to_string(cmdId) << ", ACK_ID: " << ack_id << ", ACK_DELAY: 1}";  
	cout << "EXITCONTROL: " << message.str() << endl; 
        publisher->publish_message(queue, message.str()); 
    }
    os_nanoSleep(delay_10ms);
} 
string CommandListener::get_next_timed_ack_id(string ack_type) { 
    next_timed_ack_id = next_timed_ack_id + 1; 
    string ack = to_string(next_timed_ack_id); 
    string formatted_ack = string(6 - ack.length(), '0') + ack; 
    string retval = ack_type + "_" + formatted_ack; 
    return retval; 
}

int main() { 
    CommandListener cmd; 
    pthread_exit(NULL); 
    return 0; 
} 
