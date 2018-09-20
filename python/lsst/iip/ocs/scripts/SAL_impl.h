#include <iostream> 
#include "SAL_atArchiver.h"
#include "SAL_archiver.h"
#include <map>
#include <boost/variant.hpp>

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
        SAL() { 
            ar = AR(); 
            at = AT();
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
            instance.state = 0;

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
