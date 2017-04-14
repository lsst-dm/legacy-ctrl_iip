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

using namespace std;

int next_timed_ack_id = 0; 

template <typename T, typename U> 
using funcptr = int (T::*)(U*); 

template <typename SAL_device, typename SAL_struct>
void listenCommand(string device, string command_name, os_time delay_10ms, int cmdId, 
SimplePublisher* publisher, string publish_q, string consume_q, SAL_device mgr, funcptr<SAL_device, SAL_struct> acceptCommand){ 
    SAL_struct SALInstance; 
    cmdId = (mgr.*acceptCommand)(&SALInstance); 
    if (cmdId > 0) { 
	cout << "== " << device << " " << command_name << " Command" << endl; 
	ostringstream ack_msg; 
	string ack_id = CommandListener::get_next_timed_ack_id(command_name); 
	ack_msg << "{ MSG_TYPE: " << command_name 
		<< ", DEVICE: " << device 
		<< ", CMD_ID: " << to_string(cmdId) 
		<< ", ACK_ID: " << ack_id
		<< ", ACK_DELAY: 2}"; 
	cout << "XXX NORMAL: " << command_name << ": " << ack_msg.str() << endl; 

	ostringstream book_keeping; 
	book_keeping << "{ MSG_TYPE: BOOK_KEEPING"
		     << ", ACK_ID: " << ack_id 
		     << ", ACK_DELAY: 2" 
		     << ", CHECKBOX: false" 
                     << ", TIME: " << get_current_time()
	             << ", CMD_ID: " << to_string(cmdId) 
		     << ", DEVICE: " << device << "}"; 
	cout << "XXX BOOK_KEEPING: " << book_keeping.str() << endl; 

	publisher->publish_message(consume_q, book_keeping.str()); 
	publisher->publish_message(publish_q, ack_msg.str());  
    }
    os_nanoSleep(delay_10ms); 
}  

template <typename SAL_device, typename SAL_struct>
void listenCommand_start(string device, string command_name, os_time delay_10ms, int cmdId, 
SimplePublisher* publisher, string publish_q, string consume_q, SAL_device mgr, funcptr<SAL_device, SAL_struct> acceptCommand){ 
    SAL_struct SALInstance; 
    cmdId = (mgr.*acceptCommand)(&SALInstance); 
    if (cmdId > 0) { 
	cout << "== " << device << " " << command_name << " Command" << endl; 
	ostringstream ack_msg; 
	string ack_id = CommandListener::get_next_timed_ack_id(command_name); 
	ack_msg << "{ MSG_TYPE: " << command_name 
		<< ", DEVICE: " << device 
		<< ", CMD_ID: " << to_string(cmdId) 
		<< ", ACK_ID: " << ack_id
		<< ", CFG_KEY: " << SALInstance.configuration
		<< ", ACK_DELAY: 2}"; 
	cout << "XXX NORMAL: " << command_name << ": " << ack_msg.str() << endl; 

	ostringstream book_keeping; 
	book_keeping << "{ MSG_TYPE: BOOK_KEEPING"
		     << ", ACK_ID: " << ack_id 
		     << ", ACK_DELAY: 2" 
		     << ", CHECKBOX: false" 
                     << ", TIME: " << get_current_time()
	             << ", CMD_ID: " << to_string(cmdId) 
		     << ", DEVICE: " << device << "}"; 
	cout << "XXX BOOK_KEEPING: " << book_keeping.str() << endl; 

	publisher->publish_message(consume_q, book_keeping.str()); 
	publisher->publish_message(publish_q, ack_msg.str());  
    }
    os_nanoSleep(delay_10ms); 
}  

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
	rabbit_publisher->publish_message("dmcs_ocs_publish", "{MSG_TYPE: RESOLVE_ACK}"); 
	usleep(3000000);
    }  
    return 0; 
} 

void *CommandListener::run_ocs_consumer(void *pargs) { 
    ocs_thread_args *params = ((ocs_thread_args *)pargs); 
    SAL_archiver archiver = params->archie; 
    SAL_catchuparchiver catchuparchiver = params->catchuparchie; 
    SAL_processingcluster processingcluster = params->processie; 
    SimplePublisher* rabbit_publisher = params->publisher; 
    string queue = params->queue; 
    
    os_time delay_10ms = {0, 10000000}; 

    int cmdId = -1;

    archiver.salProcessor("archiver_command_start"); 
    archiver.salProcessor("archiver_command_stop"); 
    archiver.salProcessor("archiver_command_enable"); 
    archiver.salProcessor("archiver_command_disable"); 
    archiver.salProcessor("archiver_command_standby"); 
    archiver.salProcessor("archiver_command_enterControl"); 
    archiver.salProcessor("archiver_command_exitControl"); 
    archiver.salProcessor("archiver_command_abort"); 

    catchuparchiver.salProcessor("catchuparchiver_command_start"); 
    catchuparchiver.salProcessor("catchuparchiver_command_stop"); 
    catchuparchiver.salProcessor("catchuparchiver_command_enable"); 
    catchuparchiver.salProcessor("catchuparchiver_command_disable"); 
    catchuparchiver.salProcessor("catchuparchiver_command_standby"); 
    catchuparchiver.salProcessor("catchuparchiver_command_enterControl"); 
    catchuparchiver.salProcessor("catchuparchiver_command_exitControl"); 
    catchuparchiver.salProcessor("catchuparchiver_command_abort"); 

    processingcluster.salProcessor("processingcluster_command_start"); 
    processingcluster.salProcessor("processingcluster_command_stop"); 
    processingcluster.salProcessor("processingcluster_command_enable"); 
    processingcluster.salProcessor("processingcluster_command_disable"); 
    processingcluster.salProcessor("processingcluster_command_standby"); 
    processingcluster.salProcessor("processingcluster_command_enterControl"); 
    processingcluster.salProcessor("processingcluster_command_exitControl"); 
    processingcluster.salProcessor("processingcluster_command_abort"); 
    cout << "=== dm COMMAND controller ready" << endl; 

    funcptr<SAL_archiver, archiver_command_startC> ar_start = &SAL_archiver::acceptCommand_start; 
    funcptr<SAL_archiver, archiver_command_stopC> ar_stop = &SAL_archiver::acceptCommand_stop; 
    funcptr<SAL_archiver, archiver_command_enableC> ar_enable = &SAL_archiver::acceptCommand_enable; 
    funcptr<SAL_archiver, archiver_command_disableC> ar_disable = &SAL_archiver::acceptCommand_disable; 
    funcptr<SAL_archiver, archiver_command_standbyC> ar_standby = &SAL_archiver::acceptCommand_standby; 
    funcptr<SAL_archiver, archiver_command_enterControlC> ar_enterControl = &SAL_archiver::acceptCommand_enterControl; 
    funcptr<SAL_archiver, archiver_command_exitControlC> ar_exitControl = &SAL_archiver::acceptCommand_exitControl; 
    funcptr<SAL_archiver, archiver_command_abortC> ar_abort = &SAL_archiver::acceptCommand_abort; 

    funcptr<SAL_catchuparchiver, catchuparchiver_command_startC> cu_start = &SAL_catchuparchiver::acceptCommand_start; 
    funcptr<SAL_catchuparchiver, catchuparchiver_command_stopC> cu_stop = &SAL_catchuparchiver::acceptCommand_stop; 
    funcptr<SAL_catchuparchiver, catchuparchiver_command_enableC> cu_enable = &SAL_catchuparchiver::acceptCommand_enable; 
    funcptr<SAL_catchuparchiver, catchuparchiver_command_disableC> cu_disable = &SAL_catchuparchiver::acceptCommand_disable; 
    funcptr<SAL_catchuparchiver, catchuparchiver_command_standbyC> cu_standby = &SAL_catchuparchiver::acceptCommand_standby; 
    funcptr<SAL_catchuparchiver, catchuparchiver_command_enterControlC> cu_enterControl = &SAL_catchuparchiver::acceptCommand_enterControl; 
    funcptr<SAL_catchuparchiver, catchuparchiver_command_exitControlC> cu_exitControl = &SAL_catchuparchiver::acceptCommand_exitControl; 
    funcptr<SAL_catchuparchiver, catchuparchiver_command_abortC> cu_abort = &SAL_catchuparchiver::acceptCommand_abort; 

    funcptr<SAL_processingcluster, processingcluster_command_startC> pp_start = &SAL_processingcluster::acceptCommand_start; 
    funcptr<SAL_processingcluster, processingcluster_command_stopC> pp_stop = &SAL_processingcluster::acceptCommand_stop; 
    funcptr<SAL_processingcluster, processingcluster_command_enableC> pp_enable = &SAL_processingcluster::acceptCommand_enable; 
    funcptr<SAL_processingcluster, processingcluster_command_disableC> pp_disable = &SAL_processingcluster::acceptCommand_disable; 
    funcptr<SAL_processingcluster, processingcluster_command_standbyC> pp_standby = &SAL_processingcluster::acceptCommand_standby; 
    funcptr<SAL_processingcluster, processingcluster_command_enterControlC> pp_enterControl = &SAL_processingcluster::acceptCommand_enterControl; 
    funcptr<SAL_processingcluster, processingcluster_command_exitControlC> pp_exitControl = &SAL_processingcluster::acceptCommand_exitControl; 
    funcptr<SAL_processingcluster, processingcluster_command_abortC> pp_abort = &SAL_processingcluster::acceptCommand_abort; 

    string publish_q = "ocs_dmcs_consume"; 
    string consume_q = "dmcs_ocs_publish"; 

    while (1) { 
	listenCommand_start<SAL_archiver, archiver_command_startC>("AR", "START", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, archiver, ar_start);  
	listenCommand<SAL_archiver, archiver_command_stopC>("AR", "STOP", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, archiver, ar_stop);  
	listenCommand<SAL_archiver, archiver_command_enableC>("AR", "ENABLE", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, archiver, ar_enable);  
	listenCommand<SAL_archiver, archiver_command_disableC>("AR", "DISABLE", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, archiver, ar_disable);  
	listenCommand<SAL_archiver, archiver_command_standbyC>("AR", "STANDBY", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, archiver, ar_standby);  
	listenCommand<SAL_archiver, archiver_command_enterControlC>("AR", "ENTERCONTROL", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, archiver, ar_enterControl);
	listenCommand<SAL_archiver, archiver_command_exitControlC>("AR", "EXITCONTROL", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, archiver, ar_exitControl);  
	listenCommand<SAL_archiver, archiver_command_abortC>("AR", "ABORT", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, archiver, ar_abort);  

	listenCommand_start<SAL_catchuparchiver, catchuparchiver_command_startC>("CU", "START", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, catchuparchiver, cu_start);  
	listenCommand<SAL_catchuparchiver, catchuparchiver_command_stopC>("CU", "STOP", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, catchuparchiver, cu_stop);  
	listenCommand<SAL_catchuparchiver, catchuparchiver_command_enableC>("CU", "ENABLE", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, catchuparchiver, cu_enable);  
	listenCommand<SAL_catchuparchiver, catchuparchiver_command_disableC>("CU", "DISABLE", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, catchuparchiver, cu_disable);  
	listenCommand<SAL_catchuparchiver, catchuparchiver_command_standbyC>("CU", "STANDBY", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, catchuparchiver, cu_standby);  
	listenCommand<SAL_catchuparchiver, catchuparchiver_command_enterControlC>("CU", "ENTERCONTROL", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, catchuparchiver, cu_enterControl);
	listenCommand<SAL_catchuparchiver, catchuparchiver_command_exitControlC>("CU", "EXITCONTROL", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, catchuparchiver, cu_exitControl);  
	listenCommand<SAL_catchuparchiver, catchuparchiver_command_abortC>("CU", "ABORT", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, catchuparchiver, cu_abort);  

	listenCommand_start<SAL_processingcluster, processingcluster_command_startC>("PP", "START", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, processingcluster, pp_start);  
	listenCommand<SAL_processingcluster, processingcluster_command_stopC>("PP", "STOP", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, processingcluster, pp_stop);  
	listenCommand<SAL_processingcluster, processingcluster_command_enableC>("PP", "ENABLE", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, processingcluster, pp_enable);  
	listenCommand<SAL_processingcluster, processingcluster_command_disableC>("PP", "DISABLE", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, processingcluster, pp_disable);  
	listenCommand<SAL_processingcluster, processingcluster_command_standbyC>("PP", "STANDBY", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, processingcluster, pp_standby);  
	listenCommand<SAL_processingcluster, processingcluster_command_enterControlC>("PP", "ENTERCONTROL", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, processingcluster, pp_enterControl);
	listenCommand<SAL_processingcluster, processingcluster_command_exitControlC>("PP", "EXITCONTROL", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, processingcluster, pp_exitControl);  
	listenCommand<SAL_processingcluster, processingcluster_command_abortC>("PP", "ABORT", delay_10ms, 
	    cmdId, rabbit_publisher, publish_q, consume_q, processingcluster, pp_abort);  
    }
    archiver.salShutdown(); 
    catchuparchiver.salShutdown(); 
    processingcluster.salShutdown();
    return 0;
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
