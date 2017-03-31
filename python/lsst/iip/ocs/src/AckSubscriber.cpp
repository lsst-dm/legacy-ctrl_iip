#include <functional> 
#include <ctime> 
#include <string.h>
#include <iostream> 
#include <yaml-cpp/yaml.h>
#include <boost/variant.hpp> 
#include "SAL_archiver.h"
#include "SAL_catchuparchiver.h" 
#include "SAL_processingcluster.h"
#include "unistd.h"
#include "OCS_Bridge.h"
#include "AckSubscriber.h"
#include "Toolsmod.h"

using namespace std; 
using namespace YAML; 


template<class T> 
class SAL { 
    public: 
    typedef salReturn (T::*funcptr)(int, salLONG, salLONG, char *); 

    map<string, funcptr> action_handler = { 
	{"START_ACK", &T::ackCommand_start}, 
	{"STOP_ACK", &T::ackCommand_stop}, 
	{"ENABLE_ACK", &T::ackCommand_enable}, 
	{"DISABLE_ACK", &T::ackCommand_disable}, 
	{"ENTERCONTROL_ACK", &T::ackCommand_enterControl}, 
	{"STANDBY_ACK", &T::ackCommand_standby}, 
	{"EXITCONTROL_ACK", &T::ackCommand_exitControl}, 
	{"ABORT_ACK", &T::ackCommand_abort}
    }; 
};  

struct visitor : public boost::static_visitor<> { 
    template <typename T> 
	void operator() (T &op) const { 
	    SAL<T> t; 
	    typename SAL<T>::funcptr action = t.action_handler[dict_key]; 
	    op.salProcessor(const_cast<char *>(cmd.c_str())); 
	    (op.*action)(cmdId, SAL__CMD_COMPLETE, error_code, const_cast<char *>(ack_statement.c_str()));
	}
	
	string dict_key; 
	string cmd; 
	int cmdId; 
	salLONG error_code; 
	string ack_statement;  
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
    
    if (message_value == "BOOK_KEEPING") { 
	string ack_delay = node["ACK_DELAY"].as<string>(); 
	string ack_id = node["ACK_ID"].as<string>(); 
	string time = node["TIME"].as<string>(); 
	string checkbox = node["CHECKBOX"].as<string>(); 
	string cmdId = node["CMD_ID"].as<string>(); 
	string device = node["DEVICE"].as<string>(); 

	map<string, string> innerdict; 
	innerdict["ACK_DELAY"] = ack_delay; 
	innerdict["TIME"] = time; 
	innerdict["CHECKBOX"] = checkbox; 
	innerdict["CMD_ID"] = cmdId; 
	innerdict["DEVICE"] = device; 

	ack_book_keeper[ack_id] = innerdict; 
	cout << "BOOKKEEPING: " << cmdId << endl; 
    } 
    else if (message_value == "RESOLVE_ACK") { 
	for (auto &ack_dict : ack_book_keeper) { 
	    string check_box = ack_dict.second.find("CHECKBOX")->second; 
	    string device = ack_dict.second.find("DEVICE")->second; 
	    string ack_id = ack_dict.first; 

	    if (check_box == "false") { 
		string dict_time = ack_dict.second.find("TIME")->second; 
		string ack_delay = ack_dict.second.find("ACK_DELAY")->second; 

		int time_delta = get_time_delta(dict_time); 
		bool timeout_result = time_delta > stoi(ack_delay) ? true : false; 

		if (timeout_result) { 
		    string cmd_id = ack_dict.second.find("CMD_ID")->second; 
		    int command_id = stoi(cmd_id); 
		    
		    string ack_id = ack_dict.first; 
		    string construct_msg = ack_id.substr(0, ack_id.find("_")) + "_ACK";  
		    string cmd = get_salProcessor(device, ack_id); 
		    
		    visitor v; 
		    v.dict_key = construct_msg; 
		    v.cmd = cmd; 
		    v.cmdId = command_id; 
		    v.error_code = -302; 
		    v.ack_statement = "DONE: OK"; 

		    cout << "XXX PRINT: " << device << "::" << ack_id << "::" << cmd << "::" << v.ack_statement << endl; 
		    sal_obj mgr = get_SALObj(device); 
		    boost::apply_visitor(v, mgr); 

		    ack_book_keeper[ack_id]["CHECKBOX"] = "true";
		}  	
	    }  
	}
    } 
    else { 
	cmdId = stoi(node["CMD_ID"].as<string>()); 
	string device = node["DEVICE"].as<string>(); 
	string ack_id = node["ACK_ID"].as<string>(); 
	string ack_bool = node["ACK_BOOL"].as<string>(); 
	string ack_statement = node["ACK_STATEMENT"].as<string>(); 
	string cmd = get_salProcessor(device, ack_id); 

	visitor v; 
	v.dict_key = message_value; 
	v.cmdId = cmdId; 
	v.cmd = cmd; 
	v.error_code = (ack_bool == "true") ? 0: -302; 
	v.ack_statement = ack_statement; 
	
	cout << "XXX PRINT2: " << cmdId << "::" << device << "::" << ack_id << "::" << cmd << "::" << v.ack_statement << endl; 
	sal_obj mgr = get_SALObj(device); 
	boost::apply_visitor(v, mgr); 
	
	ack_book_keeper[ack_id]["CHECKBOX"] = "true"; 
    } 
} 

string AckSubscriber::get_salProcessor(string device, string ack_id) { 
    cout << "XXX GET_SAL: " << device << "::" << ack_id << endl; 
    string command = ack_id.substr(0, ack_id.find("_")); 
    transform(command.begin(), command.end(), command.begin(), ::tolower); 
    string device_name; 
	
    if (device == "AR") { device_name = "archiver"; } 
    else if (device == "CU") { device_name = "catchuparchiver"; } 
    else { device_name = "processingcluster"; } 

    string cmd = device_name + "_command_" + command; 

    return cmd; 
} 

AckSubscriber::sal_obj AckSubscriber::get_SALObj(string device) { 
    sal_obj my_device; 
    if (device == "AR") my_device = SAL_archiver(); 
    else if (device == "CU") my_device = SAL_catchuparchiver(); 
    else my_device = SAL_processingcluster(); 
    return my_device;  
} 

int main() { 
    AckSubscriber ack; 
    ack.run(); 
    return 0; 
} 
