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

typedef void (*funcptr)(Node); 
    
template <typename T, typename U> 
class eventSAL { 
    public: 
    typedef salReturn (T::*eventStateFunc)(U*, int); 
    void send_eventState(Node n, eventStateFunc logEvent, U data) { 
	string message_type, device; 
	int priority; 
	try { 
	    message_type = n["MSG_TYPE"].as<string>(); 
	    device = n["DEVICE"].as<string>(); 
	    priority = n["PRIORITY"].as<int>();
	    T mgr = T(); 
	    string sal_event = AckSubscriber::get_salEvent(device, message_type); 
	    mgr.salEvent(const_cast<char *>(sal_event.c_str())); 
	    (mgr.*logEvent)(&data, priority);  
	    mgr.salShutdown(); 
	} 
	catch (exception& e) { 
	    cout << "WARNING: In AckSubscriber -- send_eventState, cannot read fields from message." << endl; 
	}
    } 
}; 

template<typename T> 
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

map<string, funcptr> action_handler = { 
    {"START_ACK", &AckSubscriber::process__ack}, 
    {"STOP_ACK", &AckSubscriber::process__ack}, 
    {"ENABLE_ACK", &AckSubscriber::process__ack}, 
    {"DISABLE_ACK", &AckSubscriber::process__ack}, 
    {"ENTERCONTROL_ACK", &AckSubscriber::process__ack}, 
    {"STANDBY_ACK", &AckSubscriber::process__ack}, 
    {"EXITCONTROL_ACK", &AckSubscriber::process__ack}, 
    {"ABORT_ACK", &AckSubscriber::process__ack}, 
    {"SUMMARY_STATE", &AckSubscriber::process_event__SummaryState}, 
    {"RECOMMENDED_SETTING_VERSIONS", &AckSubscriber::process_event__RecommendedSettings}, 
    {"SETTINGS_APPLIED", &AckSubscriber::process_event__AppliedSettings}, 
    {"APPLIED_SETTINGS_MATCHSTART", &AckSubscriber::process_event__AppliedSettingsMatchStart}, 
    {"ERROR_CODE", &AckSubscriber::process_event__ErrorCode}, 
    {"BOOK_KEEPING", &AckSubscriber::process__book_keeping}, 
    {"RESOLVE_ACK", &AckSubscriber::process__resolve_ack}
}; 

map<string, string> eventDict = { 
    {"ERROR_CODE", "ErrorCode"}, 
    {"APPLIED_SETTINGS_MATCHSTART", "AppliedSettingsMatchStart"}, 
    {"SUMMARY_STATE", "EntitySummaryState"}, 
    {"RECOMMENDED_SETTING_VERSIONS", "SettingVersions"} 
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
    cout << "XXX MSG: " << message << endl; 
    Node node = Load(message); 
    string message_value; 
    try { 
	message_value = node["MSG_TYPE"].as<string>(); 
	funcptr action = action_handler[message_value]; 
	(*action)(node); 
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- on_message, cannot read fields from message." << endl; 
    } 
} 

void AckSubscriber::process__ack(Node n) {
    try { 
	string message_value = n["MSG_TYPE"].as<string>(); 
	int cmdId = stoi(n["CMD_ID"].as<string>()); 
	string device = n["DEVICE"].as<string>(); 
	string ack_id = n["ACK_ID"].as<string>(); 
	string ack_bool = n["ACK_BOOL"].as<string>(); 
	string ack_statement = n["ACK_STATEMENT"].as<string>();
	string cmd = get_salProcessor(device, ack_id); 

	visitor v; 
	v.dict_key = message_value; 
	v.cmdId = cmdId; 
	v.cmd = cmd; 
	v.error_code = (ack_bool == "true") ? 0: -302; 
	v.ack_statement = ack_statement; 
	
	cout << "XXX PROCESS_ACK: " << cmdId << "::" << device << "::" << ack_id << "::" << cmd << "::" << v.ack_statement << endl; 
	sal_obj mgr = get_salObj(device); 
	boost::apply_visitor(v, mgr); 
	
	ack_book_keeper[ack_id]["CHECKBOX"] = "true"; 
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- process__ack, cannot read fields from message." << endl; 
    } 
}
 
void AckSubscriber::process_event__SummaryState(Node n) {
    string device, name, timestamp, current_state, previous_state, executing, commands_available, configurations_available;
    double identifier; 
    long priority, address; 
    try { 
	device = n["DEVICE"].as<string>(); 
	name = n["NAME"].as<string>(); 
	identifier = n["IDENTIFIER"].as<double>(); 
	timestamp = n["TIMESTAMP"].as<string>(); 
	address = n["ADDRESS"].as<long>(); 
	current_state = n["CURRENT_STATE"].as<string>(); 
	previous_state = n["PREVIOUS_STATE"].as<string>(); 
	executing = n["EXECUTING"].as<string>();  
	commands_available = n["COMMANDS_AVAILABLE"].as<string>();  
	configurations_available = n["CONFIGURATIONS_AVAILABLE"].as<string>();  
	priority = n["PRIORITY"].as<long>();  
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In Acksubscriber -- process_event__SummaryState, cannot read fields from message." << endl; 
	return; 
    } 
    if (device == "AR") { 
	eventSAL<SAL_archiver, archiver_logevent_archiverEntitySummaryStateC> archiver_sum; 
	eventSAL<SAL_archiver, archiver_logevent_archiverEntitySummaryStateC>::
		eventStateFunc func = &SAL_archiver::logEvent_archiverEntitySummaryState; 
	archiver_logevent_archiverEntitySummaryStateC data; 

	data.Name = name; 
	data.Identifier = identifier; 
	data.Timestamp = timestamp; 
	data.Address = address; 
	data.CurrentState = current_state; 
	data.PreviousState = previous_state; 
	data.Executing = executing;  
	data.CommandsAvailable = commands_available;  
	data.ConfigurationsAvailable = configurations_available;  
	data.priority = priority;  
	archiver_sum.send_eventState(n, func, data);  
    } 
    else if (device == "CU") { 
	eventSAL<SAL_catchuparchiver, catchuparchiver_logevent_catchuparchiverEntitySummaryStateC> catchuparchiver_sum; 
	eventSAL<SAL_catchuparchiver, catchuparchiver_logevent_catchuparchiverEntitySummaryStateC>::
		eventStateFunc func = &SAL_catchuparchiver::logEvent_catchuparchiverEntitySummaryState; 
	catchuparchiver_logevent_catchuparchiverEntitySummaryStateC data; 
	data.Name = name; 
	data.Identifier = identifier; 
	data.Timestamp = timestamp; 
	data.Address = address; 
	data.CurrentState = current_state; 
	data.PreviousState = previous_state; 
	data.Executing = executing;  
	data.CommandsAvailable = commands_available;  
	data.ConfigurationsAvailable = configurations_available;  
	data.priority = priority;  
	catchuparchiver_sum.send_eventState(n, func, data);  
    } 
    else if (device == "PP") { 
	eventSAL<SAL_processingcluster, processingcluster_logevent_processingclusterEntitySummaryStateC> processingcluster_sum; 
	eventSAL<SAL_processingcluster, processingcluster_logevent_processingclusterEntitySummaryStateC>::
		eventStateFunc func = &SAL_processingcluster::logEvent_processingclusterEntitySummaryState; 
	processingcluster_logevent_processingclusterEntitySummaryStateC data; 
	data.Name = name; 
	data.Identifier = identifier; 
	data.Timestamp = timestamp; 
	data.Address = address; 
	data.CurrentState = current_state; 
	data.PreviousState = previous_state; 
	data.Executing = executing;  
	data.CommandsAvailable = commands_available;  
	data.ConfigurationsAvailable = configurations_available;  
	data.priority = priority;  
	processingcluster_sum.send_eventState(n, func, data);  
    } 
} 

void AckSubscriber::process_event__RecommendedSettings(Node n){ 
    string device, recommended_setting_version;
    long priority; 
    try { 
	device = n["DEVICE"].as<string>();  
	recommended_setting_version = n["RECOMMENDED_SETTING_VERSION"].as<string>(); 
	priority = n["PRIORITY"].as<long>(); 
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In Acksubscriber -- process_event__RecommendedSettings, cannot read fields from message." << endl; 
	return; 
    } 
    
    if (device == "AR") { 
	eventSAL<SAL_archiver, archiver_logevent_SettingVersionsC> archiver_sum; 
	eventSAL<SAL_archiver, archiver_logevent_SettingVersionsC>::
		eventStateFunc func = &SAL_archiver::logEvent_SettingVersions; 
	archiver_logevent_SettingVersionsC data; 
	data.recommendedSettingVersion = recommended_setting_version;
	data.priority = priority;  
	archiver_sum.send_eventState(n, func, data);  
    } 
    else if (device == "CU") { 
	eventSAL<SAL_catchuparchiver, catchuparchiver_logevent_SettingVersionsC> catchuparchiver_sum; 
	eventSAL<SAL_catchuparchiver, catchuparchiver_logevent_SettingVersionsC>::
		eventStateFunc func = &SAL_catchuparchiver::logEvent_SettingVersions; 
	catchuparchiver_logevent_SettingVersionsC data; 
	data.recommendedSettingVersion = recommended_setting_version; 
	data.priority = priority;  
	catchuparchiver_sum.send_eventState(n, func, data);  
    } 
    else if (device == "PP") { 
	eventSAL<SAL_processingcluster, processingcluster_logevent_SettingVersionsC> processingcluster_sum; 
	eventSAL<SAL_processingcluster, processingcluster_logevent_SettingVersionsC>::
		eventStateFunc func = &SAL_processingcluster::logEvent_SettingVersions; 
	processingcluster_logevent_SettingVersionsC data; 
	data.recommendedSettingVersion = recommended_setting_version;
	data.priority = priority;  
	processingcluster_sum.send_eventState(n, func, data);  
    } 
}

void AckSubscriber::process_event__AppliedSettings(Node n){ 
}

void AckSubscriber::process_event__AppliedSettingsMatchStart(Node n){ 
    string device;
    bool applied_settings_matchstart_istrue;
    long priority; 
    try {
	device = n["DEVICE"].as<string>();
	applied_settings_matchstart_istrue = n["APPLIED_SETTINGS_MATCHSTART_ISTRUE"].as<bool>(); 
	priority = n["PRIORITY"].as<long>(); 
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In Acksubscriber -- process_event__AppliedSettingsMatchStart, cannot read fields from message." << endl; 
	return; 
    } 
    if (device == "AR") { 
	eventSAL<SAL_archiver, archiver_logevent_AppliedSettingsMatchStartC> archiver_sum; 
	eventSAL<SAL_archiver, archiver_logevent_AppliedSettingsMatchStartC>::
		eventStateFunc func = &SAL_archiver::logEvent_AppliedSettingsMatchStart; 
	archiver_logevent_AppliedSettingsMatchStartC data; 
	data.appliedSettingsMatchStartIsTrue = applied_settings_matchstart_istrue; 
	data.priority = priority;  
	archiver_sum.send_eventState(n, func, data);  
    } 
    else if (device == "CU") { 
	eventSAL<SAL_catchuparchiver, catchuparchiver_logevent_AppliedSettingsMatchStartC> catchuparchiver_sum; 
	eventSAL<SAL_catchuparchiver, catchuparchiver_logevent_AppliedSettingsMatchStartC>::
		eventStateFunc func = &SAL_catchuparchiver::logEvent_AppliedSettingsMatchStart; 
	catchuparchiver_logevent_AppliedSettingsMatchStartC data; 
	data.appliedSettingsMatchStartIsTrue = applied_settings_matchstart_istrue; 
	data.priority = priority;  
	catchuparchiver_sum.send_eventState(n, func, data);  
    } 
    else if (device == "PP") { 
	eventSAL<SAL_processingcluster, processingcluster_logevent_AppliedSettingsMatchStartC> processingcluster_sum; 
	eventSAL<SAL_processingcluster, processingcluster_logevent_AppliedSettingsMatchStartC>::
		eventStateFunc func = &SAL_processingcluster::logEvent_AppliedSettingsMatchStart; 
	processingcluster_logevent_AppliedSettingsMatchStartC data; 
	data.appliedSettingsMatchStartIsTrue = applied_settings_matchstart_istrue; 
	data.priority = priority;  
	processingcluster_sum.send_eventState(n, func, data);  
    } 
}

void AckSubscriber::process_event__ErrorCode(Node n){ 
    string device; 
    long error_code, priority; 
    try { 
	device = n["DEVICE"].as<string>();  
	error_code = n["ERROR_CODE"].as<long>(); 
	priority = n["PRIORITY"].as<long>(); 
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In Acksubscriber -- process_event__ErrorCode, cannot read fields from message." << endl; 
	return; 
    }
    if (device == "AR") { 
	eventSAL<SAL_archiver, archiver_logevent_ErrorCodeC> archiver_sum; 
	eventSAL<SAL_archiver, archiver_logevent_ErrorCodeC>::
		eventStateFunc func = &SAL_archiver::logEvent_ErrorCode; 
	archiver_logevent_ErrorCodeC data; 
	data.errorCode = error_code; 
	data.priority = priority;  
	archiver_sum.send_eventState(n, func, data);  
    } 
    else if (device == "CU") { 
	eventSAL<SAL_catchuparchiver, catchuparchiver_logevent_ErrorCodeC> catchuparchiver_sum; 
	eventSAL<SAL_catchuparchiver, catchuparchiver_logevent_ErrorCodeC>::
		eventStateFunc func = &SAL_catchuparchiver::logEvent_ErrorCode; 
	catchuparchiver_logevent_ErrorCodeC data; 
	data.errorCode = error_code; 
	data.priority = priority;  
	catchuparchiver_sum.send_eventState(n, func, data);  
    } 
    else if (device == "PP") { 
	eventSAL<SAL_processingcluster, processingcluster_logevent_ErrorCodeC> processingcluster_sum; 
	eventSAL<SAL_processingcluster, processingcluster_logevent_ErrorCodeC>::
		eventStateFunc func = &SAL_processingcluster::logEvent_ErrorCode; 
	processingcluster_logevent_ErrorCodeC data; 
	data.errorCode = error_code; 
	data.priority = priority;  
	processingcluster_sum.send_eventState(n, func, data);  
    } 
}

void AckSubscriber::process__resolve_ack(Node n) { 
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

		cout << "XXX RESOLVE_ACK: " << device << "::" << ack_id << "::" << cmd << "::" << v.ack_statement << endl; 
		sal_obj mgr = get_salObj(device); 
		boost::apply_visitor(v, mgr); 

		ack_book_keeper[ack_id]["CHECKBOX"] = "true";
	    }  	
	}  
    }
}

void AckSubscriber::process__book_keeping(Node n) { 
    try { 
	string ack_delay = n["ACK_DELAY"].as<string>(); 
	string ack_id = n["ACK_ID"].as<string>(); 
	string time = n["TIME"].as<string>(); 
	string checkbox = n["CHECKBOX"].as<string>(); 
	string cmdId = n["CMD_ID"].as<string>(); 
	string device = n["DEVICE"].as<string>(); 

	map<string, string> innerdict; 
	innerdict["ACK_DELAY"] = ack_delay; 
	innerdict["TIME"] = time; 
	innerdict["CHECKBOX"] = checkbox; 
	innerdict["CMD_ID"] = cmdId; 
	innerdict["DEVICE"] = device; 

	ack_book_keeper[ack_id] = innerdict; 
	cout << "XXX BOOKKEEPING: " << cmdId << endl; 
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- process__book_keeping, cannot read fields from message.";  
    } 
} 

AckSubscriber::sal_obj AckSubscriber::get_salObj(string device) { 
    sal_obj my_device; 
    if (device == "AR") my_device = SAL_archiver(); 
    else if (device == "CU") my_device = SAL_catchuparchiver(); 
    else my_device = SAL_processingcluster(); 
    return my_device; 
} 

string AckSubscriber::get_salProcessor(string device, string ack_id) { 
    string command = ack_id.substr(0, ack_id.find("_")); 
    transform(command.begin(), command.end(), command.begin(), ::tolower); 
    string device_name; 
	
    if (device == "AR") { device_name = "archiver"; } 
    else if (device == "CU") { device_name = "catchuparchiver"; } 
    else { device_name = "processingcluster"; } 

    string cmd = device_name + "_command_" + command; 

    return cmd; 
} 

string AckSubscriber::get_salEvent(string device, string message_type) { 
    string event_name, device_name, message_name; 
    if (device == "AR") device_name = "archiver"; 
    else if (device == "CU") device_name = "catchuparchiver"; 
    else if (device == "PP") device_name = "processingcluster"; 

    message_name = eventDict[message_type]; 
    if (message_type == "SUMMARY_STATE") { 
	event_name = device_name + "_logevent_" + device_name + message_name; 
    } 
    else { 
	event_name = device_name + "_logevent_" + message_name; 
    } 
    return event_name; 
} 


int main() { 
    AckSubscriber ack; 
    ack.run(); 
    return 0; 
} 

