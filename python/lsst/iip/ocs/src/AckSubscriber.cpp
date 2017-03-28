#include <ctime> 
#include <string.h>
#include <iostream> 
#include <yaml-cpp/yaml.h>
#include "SAL_archiver.h"
#include "SAL_catchuparchiver.h" 
#include "SAL_processingcluster.h"
#include "unistd.h"
#include "OCS_Bridge.h"
#include "AckSubscriber.h"
#include "Toolsmod.h"

using namespace std; 
using namespace YAML; 

typedef salReturn (SAL_archiver::*funcptr)(int, salLONG, salLONG, char *);

map<string, pair<string,funcptr>> action_handler = {
    {"START_ACK", make_pair("archiver_command_start", &SAL_archiver::ackCommand_start)},
    {"STOP_ACK", make_pair("archiver_command_stop", &SAL_archiver::ackCommand_stop)},
    {"ENABLE_ACK", make_pair("archiver_command_enable", &SAL_archiver::ackCommand_enable)},
    {"DISABLE_ACK", make_pair("archiver_command_disable", &SAL_archiver::ackCommand_disable)},
    {"ENTERCONTROL_ACK", make_pair("archiver_command_enterControl", &SAL_archiver::ackCommand_enterControl)},
    {"STANDBY_ACK", make_pair("archiver_command_standby", &SAL_archiver::ackCommand_standby)}, 
    {"OFFLINE_ACK", make_pair("archiver_command_exitControl", &SAL_archiver::ackCommand_exitControl)}, 
    {"FAULT_ACK", make_pair("archiver_command_abort", &SAL_archiver::ackCommand_abort)}
}; 

map<string, map<string, string>> ack_book_keeper; 

AckSubscriber::AckSubscriber() : OCS_Bridge() { 
    setup_consumer(); 
} 

AckSubscriber::~AckSubscriber() { 
}

void AckSubscriber::setup_consumer() { 
    ack_consumer = new Consumer(base_broker_addr, OCS_CONSUME); 
}

void AckSubscriber::run() { 
    cout << "============> running CONSUMER <=============" << endl; 
    ack_consumer->run(on_message); 
} 

void AckSubscriber::on_message(string message) { 
    cout << "MSG: " << message << endl; 
    string message_value; 
    int cmdId; 

    Node node = Load(message); 
    message_value = node["MSG_TYPE"].as<string>(); 
    SAL_archiver mgr = SAL_archiver();

    if (message_value == "BOOK_KEEPING") { 
	string ack_delay = node["ACK_DELAY"].as<string>(); 
	string ack_id = node["ACK_ID"].as<string>(); 
	string time = node["TIME"].as<string>(); 
	string checkbox = node["CHECKBOX"].as<string>(); 
	string cmdId = node["CMD_ID"].as<string>(); 

	map<string, string> innerdict; 
	innerdict["ACK_DELAY"] = ack_delay; 
	innerdict["TIME"] = time; 
	innerdict["CHECKBOX"] = checkbox; 
	innerdict["CMD_ID"] = cmdId; 

	ack_book_keeper[ack_id] = innerdict; 
	cout << "BOOKKEEPING: " << cmdId << endl; 
    } 
    else if (message_value == "RESOLVE_ACK") { 
	for (auto &ack_dict : ack_book_keeper) { 
	    string check_box = ack_dict.second.find("CHECKBOX")->second; 
	    string ack_id = ack_dict.first; 
	    if (check_box == "false") { 
		string dict_time = ack_dict.second.find("TIME")->second; 
		string ack_delay = ack_dict.second.find("ACK_DELAY")->second; 

		int time_delta = get_time_delta(dict_time); 
		cout << "DTIME: " << to_string(time_delta) << endl;
		bool timeout_result = time_delta > stoi(ack_delay) ? true : false; 

		if (timeout_result) { 
		    string cmd_id = ack_dict.second.find("CMD_ID")->second; 
		    int command_id = stoi(cmd_id); 
		    
		    string ack_id = ack_dict.first; 
		    string construct_msg = ack_id.substr(0, ack_id.find("_")) + "_ACK";  
		    funcptr action = get<1>(action_handler[construct_msg]); 
		    string cmd = get<0>(action_handler[construct_msg]); 

		    mgr.salProcessor(const_cast<char *>(cmd.c_str())); 
		    (mgr.*action)(command_id, SAL__CMD_COMPLETE, 0, "DONE: OK"); 

		    ack_book_keeper[ack_id]["CHECKBOX"] = "true";
		}  	
	    }  
	}
    } 
    else { 
	cmdId = stoi(node["CMD_ID"].as<string>()); 
	
	string cmd = get<0>(action_handler[message_value]); 
	if (!message_value.empty()) { 
	    mgr.salProcessor(const_cast<char *>(cmd.c_str())); 
	    funcptr action = get<1>(action_handler[message_value]); 

	    string ack_bool = node["ACK_BOOL"].as<string>(); 
	    string ack_statement = node["ACK_STATEMENT"].as<string>(); 
	    
	    if (ack_bool == "true") { 
		(mgr.*action)(cmdId, SAL__CMD_COMPLETE, 0, const_cast<char *>(ack_statement.c_str()));     
	    } 
	    else { 
		(mgr.*action)(cmdId, SAL__CMD_COMPLETE, -302, const_cast<char *>(ack_statement.c_str()));     
	    }  	

	    string ack_id = node["ACK_ID"].as<string>(); 
	    ack_book_keeper[ack_id]["CHECKBOX"] = "true"; 
	} 
	else { 
	    cout << "MSG_TYPE is not valid." << endl; 
	} 
    } 
} 

int main() { 
    AckSubscriber ack; 
    ack.run(); 
    return 0; 
} 
