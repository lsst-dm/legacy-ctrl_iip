#include <iostream> 
#include "SAL_atArchiver.h"
#include "SAL_archiver.h"
#include <map>
#include <boost/variant.hpp>
#include "SimplePublisher.h"

using namespace std; 

#define TIMEOUT 1

template<typename T> 
struct WFS { 
    using wfs_ptr = salReturn (T::*)(int, unsigned int); 
    map<string, wfs_ptr> wfs_map = { 
        { "enable", &T::waitForCompletion_enable }, 
        { "disable", &T::waitForCompletion_disable }, 
        { "enterControl", &T::waitForCompletion_enterControl }, 
        { "exitControl", &T::waitForCompletion_exitControl }, 
        { "start", &T::waitForCompletion_start }, 
        { "standby", &T::waitForCompletion_standby }, 
        { "abort", &T::waitForCompletion_abort }, 
    };
};

template<typename AR, typename AT>
class SAL { 
    public: 
        using ar_enable = int (SAL_archiver::*)(archiver_command_enableC*);
        using ar_disable = int (SAL_archiver::*)(archiver_command_disableC*);

        using at_enable = int (SAL_atArchiver::*)(atArchiver_command_enableC*); 
        using at_disable = int (SAL_atArchiver::*)(atArchiver_command_disableC*); 
        using at_enterControl = int (SAL_atArchiver::*)(atArchiver_command_enterControlC*); 
        using at_exitControl = int (SAL_atArchiver::*)(atArchiver_command_exitControlC*); 
        using at_start = int (SAL_atArchiver::*)(atArchiver_command_startC*); 
        using at_standby = int (SAL_atArchiver::*)(atArchiver_command_standbyC*); 
        using at_abort = int (SAL_atArchiver::*)(atArchiver_command_abortC*); 

        AR ar; 
        AT at; 
	SimplePublisher *publisher; 
        SAL() { 
            ar = AR(); 
            at = AT();
            // read from L1SystemCfg
            publisher = new SimplePublisher("amqp://DMCS_PUB:DMCS_PUB@140.252.32.128/%2ftest_at");
        }

        map<string, string> device_map = { 
            { "AR", "archiver" }, 
            { "CU", "catchuparchiver" }, 
            { "PP", "processingcluster" }, 
            { "AT", "atArchiver" }
        };

        string get_command_topic(string device, string command) { 
            string device_long = device_map[device];
            string topic = device_long + "_command_" + command; 
            return topic;
        } 


        typedef boost::variant<
            ar_enable,
            at_enable,
            at_disable, 
            at_enterControl, 
            at_exitControl, 
            at_start, 
            at_standby, 
            at_abort
        > issueFunctions; 

        map<pair<string, string>, issueFunctions> issue_map = { 
            { make_pair("AR", "enable"), &SAL_archiver::issueCommand_enable }, 
            { make_pair("AT", "enable"), &SAL_atArchiver::issueCommand_enable }, 
            { make_pair("AT", "disable"), &SAL_atArchiver::issueCommand_disable }, 
            { make_pair("AT", "enterControl"), &SAL_atArchiver::issueCommand_enterControl }, 
            { make_pair("AT", "exitControl"), &SAL_atArchiver::issueCommand_exitControl }, 
            { make_pair("AT", "start"), &SAL_atArchiver::issueCommand_start }, 
            { make_pair("AT", "standby"), &SAL_atArchiver::issueCommand_standby }, 
            { make_pair("AT", "abort"), &SAL_atArchiver::issueCommand_abort }, 
        };

        template<typename SALInstance> 
        void send_command(string class_name, string action) { 
            int cmdId; 
            int timeout = TIMEOUT; 
            int status = 0; 
            SALInstance instance; 
            instance.device = ""; 

            string topic = get_command_topic(class_name, action);
            cout << topic << endl;
            if (class_name == "AR") { 
                ar.salCommand(const_cast<char *>(topic.c_str())); 

                issueFunctions func = issue_map[make_pair(class_name, action)]; 
                issueCommand_visitor visitor(ar, at, instance); 
                boost::apply_visitor(visitor, func);

                WFS<AR> wfs; 
                typename WFS<AR>::wfs_ptr waitForCompletion = wfs.wfs_map[action];
                status = (ar.*waitForCompletion)(cmdId, timeout);
		if (status == 303) { // completed_ok
		     publisher->publish_message("test_dmcs_ocs_publish", 
			"{ MSG_TYPE: ENABLE_ACK, DEVICE: AR, CMD_ID: None, ACK_ID: None, ACK_BOOL: None, ACK_STATEMENT: None }");  
		} 
            } 
            else if (class_name == "AT") { 
                at.salCommand(const_cast<char *>(topic.c_str())); 

                issueFunctions func = issue_map[make_pair(class_name, action)]; 
                issueCommand_visitor visitor(ar, at, instance); 
                boost::apply_visitor(visitor, func);

                WFS<AT> wfs; 
                typename WFS<AT>::wfs_ptr waitForCompletion = wfs.wfs_map[action];
                status = (at.*waitForCompletion)(cmdId, timeout);
		if (status == 303) { // completed_ok
		     publisher->publish_message("test_dmcs_ocs_publish", 
			"{ MSG_TYPE: ENABLE_ACK, DEVICE: AR, CMD_ID: None, ACK_ID: None, ACK_BOOL: None, ACK_STATEMENT: None }");  
		} 
            }
        }

        template<typename SALInstance> 
        void send_command_start(SALInstance instance, string class_name, string action) { 
            int cmdId; 
            int timeout = TIMEOUT; 
            int status = 0; 

            string topic = get_command_topic(class_name, action);
            cout << topic << endl; if (class_name == "AR") { 
                ar.salCommand(const_cast<char *>(topic.c_str())); 

                issueFunctions func = issue_map[make_pair(class_name, action)]; 
                issueCommand_visitor visitor(ar, at, instance); 
                boost::apply_visitor(visitor, func);

                WFS<AR> wfs; 
                typename WFS<AR>::wfs_ptr waitForCompletion = wfs.wfs_map[action];
                status = (ar.*waitForCompletion)(cmdId, timeout);
            } 
            else if (class_name == "AT") { 
                at.salCommand(const_cast<char *>(topic.c_str())); 

                issueFunctions func = issue_map[make_pair(class_name, action)]; 
                issueCommand_visitor visitor(ar, at, instance); 
                boost::apply_visitor(visitor, func);

                WFS<AT> wfs; 
                typename WFS<AT>::wfs_ptr waitForCompletion = wfs.wfs_map[action];
                status = (at.*waitForCompletion)(cmdId, timeout);
            }
        }

        void log_summary_state() { 
            os_time delay_10ms = { 0, 10000000 };
            int status = -1;
            atArchiver_logevent_summaryStateC SALInstance;
            at.salEventSub("atArchiver_logevent_summaryState");
            cout << "=== Event summaryState logger ready = " << endl;
            while (1) {
                status = at.getEvent_summaryState(&SALInstance);
                if (status == SAL__OK) {
                    cout << "=== Event summaryState received = " << endl;
                    cout << "    summaryState : " << SALInstance.summaryState << endl;
                    publisher->publish_message("test_dmcs_ocs_publish", 
                        "{ MSG_TYPE: SUMMARY_STATE_EVENT, DEVICE: AT, CURRENT_STATE: None }");
                }
                os_nanoSleep(delay_10ms);
            }
            at.salShutdown();
        } 

        void log_recommended_settings_versions() { 
            os_time delay_10ms = { 0, 10000000 };
            int status = -1;
            atArchiver_logevent_settingVersionsC SALInstance;
            at.salEventSub("atArchiver_logevent_settingVersions");
            cout << "=== Event settingVersions logger ready = " << endl;
            while (1) {
                status = at.getEvent_settingVersions(&SALInstance);
                if (status == SAL__OK) {
                    cout << "=== Event settingVersions received = " << endl;
                    cout << "    recommendedSettingVersion : " << SALInstance.recommendedSettingVersion << endl;
                    publisher->publish_message("test_dmcs_ocs_publish", 
                        "{ MSG_TYPE: RECOMMENDED_SETTINGS_VERSION_EVENT, DEVICE: AT, CURRENT_STATE: None }");
                }
                os_nanoSleep(delay_10ms);
            }
            at.salShutdown();
        } 

        void log_settings_applied() { 
            os_time delay_10ms = { 0, 10000000 };
            int status = -1;
            atArchiver_logevent_settingsAppliedC SALInstance;
            at.salEventSub("atArchiver_logevent_settingsApplied");
            cout << "=== Event settingsApplied logger ready = " << endl;
            while (1) {
                status = at.getEvent_settingsApplied(&SALInstance);
                if (status == SAL__OK) {
                    cout << "=== Event settingsApplied received = " << endl;
                    cout << "    settings : " << SALInstance.settings << endl;
                    cout << "    tsXMLVersion : " << SALInstance.tsXMLVersion << endl;
                    cout << "    tsSALVersion : " << SALInstance.tsSALVersion << endl;
                    cout << "    l1dmRepoTag : " << SALInstance.l1dmRepoTag << endl;
                    publisher->publish_message("test_dmcs_ocs_publish", 
                        "{ MSG_TYPE: SETTINGS_APPLIED_EVENT, DEVICE: AT, CURRENT_STATE: None }");
                }
                os_nanoSleep(delay_10ms);
            }
            at.salShutdown();
        } 

        void log_applied_settings_match_start() { 
            os_time delay_10ms = { 0, 10000000 };
            int status = -1;
            atArchiver_logevent_appliedSettingsMatchStartC SALInstance;
            at.salEventSub("atArchiver_logevent_appliedSettingsMatchStart");
            cout << "=== Event appliedSettingsMatchStart logger ready = " << endl;
            while (1) {
                status = at.getEvent_appliedSettingsMatchStart(&SALInstance);
                if (status == SAL__OK) {
                    cout << "=== Event appliedSettingsMatchStart received = " << endl;
                    cout << "    appliedSettingsMatchStartIsTrue : " << SALInstance.appliedSettingsMatchStartIsTrue << endl;
                    publisher->publish_message("test_dmcs_ocs_publish", 
                        "{ MSG_TYPE: APPLIED_SETTINGS_MATCH_START_EVENT, DEVICE: AT, CURRENT_STATE: None }");
                }
                os_nanoSleep(delay_10ms);
            }
            at.salShutdown();
        } 

        void log_error_code() { 
            os_time delay_10ms = { 0, 10000000 };
            int status = -1;
            atArchiver_logevent_errorCodeC SALInstance;
            at.salEventSub("atArchiver_logevent_errorCode");
            cout << "=== Event errorCode logger ready = " << endl;
            while (1) {
                status = at.getEvent_errorCode(&SALInstance);
                if (status == SAL__OK) {
                    cout << "=== Event errorCode received = " << endl;
                    cout << "    errorCode : " << SALInstance.errorCode << endl;
                    publisher->publish_message("test_dmcs_ocs_publish", 
                        "{ MSG_TYPE: ERROR_CODE_EVENT, DEVICE: AR, CURRENT_STATE: None }");
                }
                os_nanoSleep(delay_10ms);
            }
            at.salShutdown();
        } 
        void log_reset_from_fault() { } 

        struct issueCommand_visitor : public boost::static_visitor<> { 
            public: 
                AR ar; 
                AT at; 
                archiver_command_enableC ar_enableC; 
                atArchiver_command_enableC at_enableC; 
                atArchiver_command_disableC at_disableC;
                atArchiver_command_enterControlC at_enterControlC;
                atArchiver_command_exitControlC at_exitControlC;
                atArchiver_command_startC at_startC;
                atArchiver_command_standbyC at_standbyC;
                atArchiver_command_abortC at_abortC;

                issueCommand_visitor(AR ar, AT at, archiver_command_enableC d) : ar(ar), at(at), ar_enableC(d) {} 
                issueCommand_visitor(AR ar, AT at, atArchiver_command_enableC d) : ar(ar), at(at), at_enableC(d) {} 
                issueCommand_visitor(AR ar, AT at, atArchiver_command_disableC d) : ar(ar), at(at), at_disableC(d) {}
                issueCommand_visitor(AR ar, AT at, atArchiver_command_enterControlC d) : ar(ar), at(at), at_enterControlC(d) {}
                issueCommand_visitor(AR ar, AT at, atArchiver_command_exitControlC d) : ar(ar), at(at), at_exitControlC(d) {}
                issueCommand_visitor(AR ar, AT at, atArchiver_command_startC d) : ar(ar), at(at), at_startC(d) {}
                issueCommand_visitor(AR ar, AT at, atArchiver_command_standbyC d) : ar(ar), at(at), at_standbyC(d) {}
                issueCommand_visitor(AR ar, AT at, atArchiver_command_abortC d) : ar(ar), at(at), at_abortC(d) {}

                void operator()(ar_enable func) { (ar.*func)(&ar_enableC); }
                void operator()(at_enable func) { (at.*func)(&at_enableC); } 
                void operator()(at_disable func) { (at.*func)(&at_disableC); }
                void operator()(at_enterControl func) { (at.*func)(&at_enterControlC); }
                void operator()(at_exitControl func) { (at.*func)(&at_exitControlC); }
                void operator()(at_start func) { (at.*func)(&at_startC); }
                void operator()(at_standby func) { (at.*func)(&at_standbyC); }
                void operator()(at_abort func) { (at.*func)(&at_abortC); }
        }; 

        void shut_down() { 
            ar.salShutdown();
            at.salShutdown();
        }
}; 
