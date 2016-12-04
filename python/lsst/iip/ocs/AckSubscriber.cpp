#include <string.h>
#include <iostream> 
#include <boost/python.hpp> 
#include <yaml-cpp/yaml.h>
#include "SAL_dm.h"
#include "ccpp_sal_dm.h" 
#include "os.h"
#include "unistd.h"
#include "AckSubscriber.h"

using namespace std; 
using namespace boost::python; 
using namespace YAML; 
using namespace dm;
using namespace DDS; 

typedef salReturn (SAL_dm::*funcptr)(int, salLONG, salLONG, char *); 
map<string, pair<string,funcptr>> action_handler = {
    {"START_ACK", make_pair("dm_command_start", &SAL_dm::ackCommand_start)},
    {"STOP_ACK", make_pair("dm_command_stop", &SAL_dm::ackCommand_stop)},
    {"ENABLE_ACK", make_pair("dm_command_enable", &SAL_dm::ackCommand_enable)},
    {"DISABLE_ACK", make_pair("dm_command_disable", &SAL_dm::ackCommand_disable)},
    {"ENTERCONTROL_ACK", make_pair("dm_command_enterControl", &SAL_dm::ackCommand_enterControl)},
    {"STANDBY_ACK", make_pair("dm_command_standby", &SAL_dm::ackCommand_standby)}, 
    {"EXITCONTROL_ACK", make_pair("dm_command_exitControl", &SAL_dm::ackCommand_exitControl)}, 
    {"ABORT_ACK", make_pair("dm_command_abort", &SAL_dm::ackCommand_abort)}
}; 
					
AckSubscriber::AckSubscriber() { 
    Node config = LoadFile("AckSubscriberCfg.yaml"); 

    string usrname = config["ROOT"]["BASE_BROKER_NAME"].as<string>(); 
    string passwd = config["ROOT"]["BASE_BROKER_PASSWD"].as<string>(); 
    string addr = config["ROOT"]["BASE_BROKER_ADDR"].as<string>(); 
    ostringstream broker_addr; 
    broker_addr << "amqp://" << usrname << ":" << passwd << "@" << addr; 
    base_broker_addr = broker_addr.str(); 

    OCS_CONSUME = config["ROOT"]["OCS_CONSUME"].as<string>(); 

    Py_Initialize(); 
    setup_consumer(); 
} 

AckSubscriber::~AckSubscriber() { 
}

void AckSubscriber::setup_consumer() { 
    object pyimport = import("Consumer");
    ocs_consumer = pyimport.attr("Consumer")(base_broker_addr, OCS_CONSUME);  
}

void AckSubscriber::run() { 
    cout << "============> running CONSUMER <=============" << endl; 
    object pymethod = make_function(AckSubscriber::on_dmcs_message);  
    ocs_consumer.attr("run")(pymethod); 
} 

void AckSubscriber::on_dmcs_message(object ch, object method, object properties, dict body) { 
    string message_type, message_value; 
    try { 
	GILRelease gil;
	cout << "#############  RECEIVING MESSAGE #############" << endl; 
	int l = len(body); 
	boost::python::list keys = body.keys(); 
	for (int i = 0; i < l; i ++) { 
	    string key = extract<string>(keys[i]); 
	    string value = extract<string>(body[keys[i]]); 
	    cout << key + ": " + value << endl;
	    if (key == "MSG_TYPE"){ 
		message_type = key; 
		message_value = value; 
	    }  
	} 
    } 
    catch (error_already_set const &) { 
	PyErr_Print(); 
    }

    SAL_dm mgr = SAL_dm();
    string cmd = get<0>(action_handler[message_value]); 
    if (!message_value.empty()) { 
	mgr.salProcessor(const_cast<char *>(cmd.c_str())); 
	funcptr action = get<1>(action_handler[message_value]); 
	(mgr.*action)(0, SAL__CMD_COMPLETE, 0, "Done: OK");     
    } 
    else { 
	cout << "MSG_TYPE is not valid." << endl; 
    } 
} 

int main() { 
    AckSubscriber ack; 
    ack.run(); 
    return 0; 
} 
