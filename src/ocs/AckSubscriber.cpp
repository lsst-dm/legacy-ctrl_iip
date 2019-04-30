/*
 * This file is part of ctrl_iip
 *
 * Developed for the LSST Data Management System.
 * This product includes software developed by the LSST Project
 * (https://www.lsst.org).
 * See the COPYRIGHT file at the top-level directory of this distribution
 * for details of code ownership.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include <string.h>
#include <iostream> 
#include <yaml-cpp/yaml.h>
#include "AckSubscriber.h"
#include "SAL_defines.h"
#include "Toolsmod.h"

BOOST_LOG_INLINE_GLOBAL_LOGGER_DEFAULT(lg, src::severity_logger_mt< severity_level >);
#include "IIPMacro.h"

using namespace std; 
using namespace YAML; 

using ack_funcptr = void (AckSubscriber::*)(Node); 

struct consumer_thread_args { 
    Consumer *consumer; 
    AckSubscriber *subscriber; 
};

map<string, map<string, string>> ack_book_keeper; 

map<string, long> summary_states = { 
    {"DISABLE", SAL__STATE_DISABLED}, 
    {"ENABLE", SAL__STATE_ENABLED}, 
    {"FAULT", SAL__STATE_FAULT}, 
    {"OFFLINE", SAL__STATE_OFFLINE}, 
    {"STANDBY", SAL__STATE_STANDBY}, 
};

map<string, ack_funcptr> action_handler = { 
    {"START_ACK", &AckSubscriber::process_ack}, 
    {"STOP_ACK", &AckSubscriber::process_ack}, 
    {"ENABLE_ACK", &AckSubscriber::process_ack}, 
    {"DISABLE_ACK", &AckSubscriber::process_ack}, 
    {"ENTER_CONTROL_ACK", &AckSubscriber::process_ack}, 
    {"STANDBY_ACK", &AckSubscriber::process_ack}, 
    {"EXIT_CONTROL_ACK", &AckSubscriber::process_ack}, 
    {"ABORT_ACK", &AckSubscriber::process_ack}, 
    {"RESET_FROM_FAULT_ACK", &AckSubscriber::process_reset_from_fault_ack}, 
    {"SUMMARY_STATE_EVENT", &AckSubscriber::process_summary_state}, 
    {"RECOMMENDED_SETTINGS_VERSION_EVENT", &AckSubscriber::process_recommended_settings_version}, 
    {"SETTINGS_APPLIED_EVENT", &AckSubscriber::process_settings_applied}, 
    {"APPLIED_SETTINGS_MATCH_START_EVENT", &AckSubscriber::process_applied_settings_match_start}, 
    {"ERROR_CODE_EVENT", &AckSubscriber::process_error_code}, 
    {"BOOK_KEEPING", &AckSubscriber::process_book_keeping}, 
    {"RESOLVE_ACK", &AckSubscriber::process_resolve_ack}
}; 

map<string, ack_funcptr> telemetry_handler = { 
    { "TELEMETRY", &AckSubscriber::process_telemetry }  
};

template<typename T> 
class Command { 
    public: 
        typedef salReturn (T::*funcptr)(int, salLONG, salLONG, char *); 

        map<string, funcptr> action_handler = { 
            {"START_ACK", &T::ackCommand_start}, 
            {"ENABLE_ACK", &T::ackCommand_enable}, 
            {"DISABLE_ACK", &T::ackCommand_disable}, 
            {"ENTER_CONTROL_ACK", &T::ackCommand_enterControl}, 
            {"STANDBY_ACK", &T::ackCommand_standby}, 
            {"EXIT_CONTROL_ACK", &T::ackCommand_exitControl}, 
            {"ABORT_ACK", &T::ackCommand_abort},
        }; 
};  

AckSubscriber::AckSubscriber() : IIPBase("L1SystemCfg.yaml", "AckSubscriber") { 
    setup_consumer(); 
} 

AckSubscriber::~AckSubscriber() { 
}

void AckSubscriber::setup_consumer() { 
    Node ocs;
    string user, passwd, publishq, consumeq, base_addr;
    try { 
        ocs = this->config_root["OCS"];
        user = this->credentials->get_user("service_user");
        passwd = this->credentials->get_passwd("service_passwd");
        publishq = ocs["OCS_PUBLISH"].as<string>();
        consumeq = ocs["OCS_CONSUME"].as<string>();
	base_addr = this->config_root["BASE_BROKER_ADDR"].as<string>(); 
    }
    catch (YAML::TypedBadConversion<string>& e) { 
	LOG_CRT << "Cannot read ocs fields from L1SystemCfg.yaml"; 
	exit(-1); 
    }
    this->base_broker_addr = this->get_amqp_url(user, passwd, base_addr);

    ack_consumer = new Consumer(this->base_broker_addr, consumeq); 
    ar = SAL_MTArchiver(); 
    cu = SAL_CatchupArchiver(); 
    pp = SAL_PromptProcessing(); 
    at = SAL_ATArchiver(); 
}

void AckSubscriber::run() { 
    // string devices[] = {"MTArchiver", "CatchupArchiver", "PromptProcessing", "ATArchiver"};
    string devices[] = {"ATArchiver"};
    string commands[] = {"enable", "disable", "standby", "enterControl", "exitControl", "start", "abort"}; 
    string events[] = {"summaryState", "appliedSettingsMatchStart", "settingVersions", "errorCode"};

    for (const string device: devices) { 
        for (const string command: commands) { 
            string topic = device + "_command_" + command;
            if (device == "MTArchiver") { 
                ar.salProcessor(const_cast<char *>(topic.c_str())); 
            } 
            else if (device == "CatchupArchiver") { 
                cu.salProcessor(const_cast<char *>(topic.c_str())); 
            } 
            else if (device == "PromptProcessing") { 
                pp.salProcessor(const_cast<char *>(topic.c_str())); 
            } 
            else if (device == "ATArchiver") { 
                at.salProcessor(const_cast<char *>(topic.c_str())); 
            } 
        }
    } 

    for (const string device: devices) { 
        for (const string event: events) { 
            string topic = device + "_logevent_" + event;
            if (device == "MTArchiver") { 
                ar.salEvent(const_cast<char *>(topic.c_str())); 
            } 
            else if (device == "CatchupArchiver") { 
                cu.salEvent(const_cast<char *>(topic.c_str())); 
            } 
            else if (device == "PromptProcessing") { 
                pp.salEvent(const_cast<char *>(topic.c_str())); 
            } 
            else if (device == "ATArchiver") { 
                at.salEventPub(const_cast<char *>(topic.c_str())); 
            } 
        }
    } 

    // These two events do not exist in other devices
    at.salProcessor(const_cast<char *>("ATArchiver_command_resetFromFault"));
    at.salEventPub(const_cast<char *>("ATArchiver_logevent_settingsApplied")); 

    // telemetry 
    at.salEventPub("ATArchiver_logevent_processingStatus");

    cout << "============> running CONSUMER <=============" << endl; 
    Consumer *telemetry_consumer = new Consumer(this->base_broker_addr, "telemetry_queue"); 

    consumer_thread_args *telemetry_args = new consumer_thread_args; 
    telemetry_args->consumer = telemetry_consumer; 
    telemetry_args->subscriber = this; 

    consumer_thread_args *ack_args = new consumer_thread_args; 
    ack_args->consumer = ack_consumer; 
    ack_args->subscriber = this; 

    pthread_create(&telemetry_t, NULL, &AckSubscriber::run_telemetry_consumer, telemetry_args); 
    pthread_create(&ack_t, NULL, &AckSubscriber::run_ack_consumer, ack_args); 
} 

void *AckSubscriber::run_telemetry_consumer(void *pargs) {
    cout << "Consuming telemetry..." << endl;
    consumer_thread_args *params = ((consumer_thread_args *)pargs); 
    Consumer *consumer = params->consumer; 
    AckSubscriber *subscriber = params->subscriber;
    callback<AckSubscriber> on_msg = &AckSubscriber::on_telemetry_message; 
    consumer->run<AckSubscriber>(subscriber, on_msg); 
    return 0;
} 

void *AckSubscriber::run_ack_consumer(void *pargs) {
    cout << "Consuming acks..." << endl;
    consumer_thread_args *params = ((consumer_thread_args *)pargs); 
    Consumer *consumer = params->consumer; 
    AckSubscriber *subscriber = params->subscriber;
    callback<AckSubscriber> on_msg = &AckSubscriber::on_message; 
    consumer->run<AckSubscriber>(subscriber, on_msg); 
    return 0;
} 

void AckSubscriber::on_telemetry_message(string message) { 
    Node node = Load(message); 
    string message_value; 
    try { 
	message_value = node["MSG_TYPE"].as<string>(); 
	ack_funcptr action = telemetry_handler[message_value]; 
	(this->*action)(node); 
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- on_telemetry_message, cannot read fields from message." << endl; 
    } 
} 

void AckSubscriber::on_message(string message) { 
    Node node = Load(message); 
    string message_value; 
    try { 
	message_value = node["MSG_TYPE"].as<string>(); 
	if (message_value != "RESOLVE_ACK"){
	    cout << "=== MSG: " << message << endl;
	    cout << "[" << message_value << "] ..." << endl; 
	}   
	ack_funcptr action = action_handler[message_value]; 
	(this->*action)(node); 
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- on_message, cannot read fields from message." << endl; 
    } 
} 

void AckSubscriber::process_ack(Node n) {
    try { 
	string message_value = n["MSG_TYPE"].as<string>(); 
	long cmdId = stol(n["CMD_ID"].as<string>()); 
	string device = n["DEVICE"].as<string>(); 
	string ack_id = n["ACK_ID"].as<string>(); 
	// string ack_bool = n["ACK_BOOL"].as<string>(); 
	int ack_bool = n["ACK_BOOL"].as<int>(); 
	string ack_statement = n["ACK_STATEMENT"].as<string>();

        // salLONG error_code = (ack_bool == "true") ? 0: -302; 
        salLONG error_code = ack_bool; 

        if (device == "AR") { 
            Command<SAL_MTArchiver> sender; 
            Command<SAL_MTArchiver>::funcptr action = sender.action_handler[message_value]; 
            (ar.*action)(cmdId, SAL__CMD_COMPLETE, error_code, const_cast<char *>(ack_statement.c_str())); 
        } 
        else if (device == "CU") { 
            Command<SAL_CatchupArchiver> sender; 
            Command<SAL_CatchupArchiver>::funcptr action = sender.action_handler[message_value]; 
            (cu.*action)(cmdId, SAL__CMD_COMPLETE, error_code, const_cast<char *>(ack_statement.c_str())); 
        } 
        else if (device == "PP"){ 
            Command<SAL_PromptProcessing> sender; 
            Command<SAL_PromptProcessing>::funcptr action = sender.action_handler[message_value]; 
            (pp.*action)(cmdId, SAL__CMD_COMPLETE, error_code, const_cast<char *>(ack_statement.c_str())); 
        }
        else if (device == "AT"){ 
            Command<SAL_ATArchiver> sender; 
            Command<SAL_ATArchiver>::funcptr action = sender.action_handler[message_value]; 
            (at.*action)(cmdId, SAL__CMD_COMPLETE, error_code, const_cast<char *>(ack_statement.c_str())); 
        }

	cout << "=== PROCESS_ACK: " << cmdId << "::" << device << "::" << ack_id 
             << "::" << message_value << "::" << ack_statement << endl; 

	ack_book_keeper[ack_id]["CHECKBOX"] = "true"; 
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- process_ack, cannot read fields from message." << endl; 
    }  
}

void AckSubscriber::process_summary_state(Node n) { 
    //try { 
        string message_value = n["MSG_TYPE"].as<string>(); 
        string device = n["DEVICE"].as<string>(); 
        string summary_state = n["CURRENT_STATE"].as<string>(); 
        long priority = 0; 

        if (device == "AR") { 
            MTArchiver_logevent_summaryStateC data; 
            data.summaryState = summary_states[summary_state]; 
            data.priority = priority; 
            ar.logEvent_summaryState(&data, priority); 
        }
        else if (device == "CU") {
            CatchupArchiver_logevent_summaryStateC data; 
            data.summaryState = summary_states[summary_state]; 
            data.priority = priority; 
            cu.logEvent_summaryState(&data, priority); 
        }
        else if (device == "PP") { 
            PromptProcessing_logevent_summaryStateC data; 
            data.summaryState = summary_states[summary_state]; 
            data.priority = priority; 
            pp.logEvent_summaryState(&data, priority); 
        }
        else if (device == "AT") { 
            ATArchiver_logevent_summaryStateC data; 
            data.summaryState = summary_states[summary_state]; 
            data.priority = priority; 
            at.logEvent_summaryState(&data, priority); 
        }
/**
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- summary_state, cannot read fields from message." << endl; 
        cout << "The error is " << e.what() << endl; 
    }  
*/
} 

void AckSubscriber::process_recommended_settings_version(Node n) { 
    try { 
        string message_value = n["MSG_TYPE"].as<string>(); 
        string device = n["DEVICE"].as<string>(); 
        string recommended_setting = n["CFG_KEY"].as<string>(); 
        long priority = 0; 

        if (device == "AR") { 
            MTArchiver_logevent_settingVersionsC data; 
            data.recommendedSettingsVersion = recommended_setting; 
            data.priority = priority; 
            ar.logEvent_settingVersions(&data, priority); 
        }
        else if (device == "CU") {
            CatchupArchiver_logevent_settingVersionsC data; 
            data.recommendedSettingsVersion = recommended_setting; 
            data.priority = priority; 
            cu.logEvent_settingVersions(&data, priority); 
        }
        else if (device == "PP") { 
            PromptProcessing_logevent_settingVersionsC data; 
            data.recommendedSettingsVersion = recommended_setting; 
            data.priority = priority; 
            pp.logEvent_settingVersions(&data, priority); 
        }
        else if (device == "AT") { 
            ATArchiver_logevent_settingVersionsC data; 
            data.recommendedSettingsVersion = recommended_setting; 
            data.priority = priority; 
            at.logEvent_settingVersions(&data, priority); 
        }
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- recommended_setting_versions, cannot read fields from message." << endl; 
        cout << "The error is " << e.what() << endl; 
    }  
}

// FIXME: CatchupArchiver and PromptProcessor have different values
void AckSubscriber::process_settings_applied(Node n) {
    try { 
        string message_value = n["MSG_TYPE"].as<string>(); 
        string device = n["DEVICE"].as<string>(); 
        string ts_sal = n["TS_SAL_VERSION"].as<string>(); 
        string ts_xml = n["TS_XML_VERSION"].as<string>(); 
        string l1_tag = n["L1_DM_REPO_TAG"].as<string>(); 
	string settings = n["SETTINGS"].as<string>();
        long priority = 0; 

        if (device == "AR") { 
            MTArchiver_logevent_settingsAppliedC data; 
	    data.settings = settings;
            data.tsSALVersion = ts_sal; 
            data.tsXMLVersion = ts_xml; 
            data.l1dmRepoTag = l1_tag; 
            ar.logEvent_settingsApplied(&data, priority); 
        }
        else if (device == "CU") {
            CatchupArchiver_logevent_settingsAppliedC data; 
            cu.logEvent_settingsApplied(&data, priority); 
        }
        else if (device == "PP") { 
            // This is not complete
            // PromptProcessing_logevent_settingsAppliedC data; 
            // pp.logEvent_settingsApplied(&data, priority); 
        }
        else if (device == "AT") { 
            ATArchiver_logevent_settingsAppliedC data; 
	    data.settings = settings;
            data.tsSALVersion = ts_sal; 
            data.tsXMLVersion = ts_xml; 
            data.l1dmRepoTag = l1_tag; 
            at.logEvent_settingsApplied(&data, priority); 
        }
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- settings_applied, cannot read fields from message." << endl; 
        cout << "The error is " << e.what() << endl; 
    }  
}

void AckSubscriber::process_applied_settings_match_start(Node n) {
    try { 
        string message_value = n["MSG_TYPE"].as<string>(); 
        string device = n["DEVICE"].as<string>(); 
        bool settings_applied = n["APPLIED"].as<bool>(); 
        long priority = 0; 

        if (device == "AR") { 
            MTArchiver_logevent_appliedSettingsMatchStartC data; 
            data.appliedSettingsMatchStartIsTrue = settings_applied; 
            data.priority = priority; 
            ar.logEvent_appliedSettingsMatchStart(&data, priority); 
        }
        else if (device == "CU") {
            CatchupArchiver_logevent_appliedSettingsMatchStartC data; 
            data.appliedSettingsMatchStartIsTrue = settings_applied; 
            data.priority = priority; 
            cu.logEvent_appliedSettingsMatchStart(&data, priority); 
        }
        else if (device == "PP") { 
            PromptProcessing_logevent_appliedSettingsMatchStartC data; 
            data.appliedSettingsMatchStartIsTrue = settings_applied; 
            data.priority = priority; 
            pp.logEvent_appliedSettingsMatchStart(&data, priority); 
        }
        else if (device == "AT") { 
            ATArchiver_logevent_appliedSettingsMatchStartC data; 
            data.appliedSettingsMatchStartIsTrue = settings_applied; 
            data.priority = priority; 
            at.logEvent_appliedSettingsMatchStart(&data, priority); 
        }
    }
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- applied_settings_match_start, cannot read fields from message." << endl; 
        cout << "The error is " << e.what() << endl; 
    }  
}

void AckSubscriber::process_error_code(Node n) {
    try {
        string message_value = n["MSG_TYPE"].as<string>(); 
        string device = n["DEVICE"].as<string>(); 
        long error_code = n["ERROR_CODE"].as<long>(); 
        long priority = 0; 

        if (device == "AR") { 
            MTArchiver_logevent_errorCodeC data; 
            data.errorCode = error_code; 
            data.priority = priority; 
            ar.logEvent_errorCode(&data, priority); 
        }
        else if (device == "CU") {
            CatchupArchiver_logevent_errorCodeC data; 
            data.errorCode = error_code; 
            data.priority = priority; 
            cu.logEvent_errorCode(&data, priority); 
        }
        else if (device == "PP") { 
            PromptProcessing_logevent_errorCodeC data; 
            data.errorCode = error_code; 
            data.priority = priority; 
            pp.logEvent_errorCode(&data, priority); 
        }
        else if (device == "AT") { 
            ATArchiver_logevent_errorCodeC data; 
            data.errorCode = error_code; 
            data.priority = priority; 
            at.logEvent_errorCode(&data, priority); 
        }
    }
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- error_code, cannot read fields from message." << endl; 
        cout << "The error is " << e.what() << endl; 
    }  
} 

void AckSubscriber::process_book_keeping(Node n) { 
    cout << "=== BOOK_KEEPING received" << endl;
    try { 
	string ack_id = n["ACK_ID"].as<string>(); 
	string time = n["TIME"].as<string>(); 
	string checkbox = n["CHECKBOX"].as<string>(); 
	string cmdId = n["CMD_ID"].as<string>(); 
	string device = n["DEVICE"].as<string>(); 
        string sub_type = n["SUB_TYPE"].as<string>(); 

	map<string, string> innerdict; 
	innerdict["TIME"] = time; 
	innerdict["CHECKBOX"] = checkbox; 
	innerdict["CMD_ID"] = cmdId; 
	innerdict["DEVICE"] = device; 
        innerdict["SUB_TYPE"] = sub_type; 

	ack_book_keeper[ack_id] = innerdict; 
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- process__book_keeping, cannot read fields from message.";  
    } 
} 

void AckSubscriber::process_resolve_ack(Node n) { 
    for (auto &ack_dict : ack_book_keeper) { 
	string check_box = ack_dict.second.find("CHECKBOX")->second; 
	string device = ack_dict.second.find("DEVICE")->second; 
	string ack_id = ack_dict.first; 

	if (check_box == "false") { 
	    string dict_time = ack_dict.second.find("TIME")->second; 
	    int ack_delay = 2; 

	    int time_delta = get_time_delta(dict_time); 
	    bool timeout_result = time_delta > ack_delay ? true : false; 

	    if (timeout_result) { 
		string cmd_id = ack_dict.second.find("CMD_ID")->second; 
		long command_id = stol(cmd_id); 
                string command = ack_dict.second.find("SUB_TYPE")->second + "_ACK"; 

		
		cout << "### RESOLVE_NAME: " << command  << "::" << device << "::" << command_id << endl; 
                Node new_msg; 
                new_msg["MSG_TYPE"] = command; 
                new_msg["CMD_ID"] = command_id; 
                new_msg["DEVICE"] = device; 
                new_msg["ACK_ID"] = ack_id; 
                new_msg["ACK_BOOL"] = "false";  
                new_msg["ACK_STATEMENT"] = "nack"; 
                
		ack_book_keeper[ack_id]["CHECKBOX"] = "true";
                process_ack(new_msg); 

	    }  	
	}  
    }
}
// ****************************************************************************
// RESET_FROM_FAULT_ACK
// ****************************************************************************
void AckSubscriber::process_reset_from_fault_ack(Node n) {
    try { 
	string message_value = n["MSG_TYPE"].as<string>(); 
	long cmdId = stol(n["CMD_ID"].as<string>()); 
	string device = n["DEVICE"].as<string>(); 
	string ack_id = n["ACK_ID"].as<string>(); 
	string ack_bool = n["ACK_BOOL"].as<string>(); 
	string ack_statement = n["ACK_STATEMENT"].as<string>();

        salLONG error_code = (ack_bool == "true") ? 0: -302; 

        Command<SAL_ATArchiver> sender; 
        at.ackCommand_resetFromFault(cmdId, SAL__CMD_COMPLETE, error_code, const_cast<char *>(ack_statement.c_str())); 

	cout << "=== PROCESS_ACK: " << cmdId << "::" << device << "::" << ack_id 
             << "::" << message_value << "::" << ack_statement << endl; 

	ack_book_keeper[ack_id]["CHECKBOX"] = "true"; 
    } 
    catch (exception& e) { 
	cout << "WARNING: " << "In AckSubscriber -- process_ack, cannot read fields from message." << endl; 
    }  
}

void AckSubscriber::process_telemetry(Node n) { 
    cout << "Entering process_telemetry function." << endl;
    try { 
        int priority = 0;
        int status_code = n["STATUS_CODE"].as<int>(); 
        string description = n["DESCRIPTION"].as<string>(); 

        ATArchiver_logevent_processingStatusC data; 
        data.statusCode = status_code; 
        data.description = description; 
        data.priority = priority; 
        at.logEvent_processingStatus(&data, priority);
    } 
    catch (exception& e) { 
        cout << "In process_telemetry, Cannot publish messages back to OCS." << endl; 
    } 
} 

int main() { 
    AckSubscriber ack; 
    ack.run(); 
    while(1) { 

        sleep(5);
    }
    return 0; 
} 
