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

/* function pointer to be used with map to handle message_types */
typedef salReturn (SAL_dm::*funcptr)(int, salLONG, salLONG, char *);

/* map of message_types and function pointer to handle callbacks */ 
map<string, pair<string,funcptr>> action_handler = {
    {"START_ACK", make_pair("dm_command_start", &SAL_dm::ackCommand_start)},
    {"STOP_ACK", make_pair("dm_command_stop", &SAL_dm::ackCommand_stop)},
    {"ENABLE_ACK", make_pair("dm_command_enable", &SAL_dm::ackCommand_enable)},
    {"DISABLE_ACK", make_pair("dm_command_disable", &SAL_dm::ackCommand_disable)},
    {"ENTERCONTROL_ACK", make_pair("dm_command_enterControl", &SAL_dm::ackCommand_enterControl)},
    {"STANDBY_ACK", make_pair("dm_command_standby", &SAL_dm::ackCommand_standby)}, 
    {"OFFLINE_ACK", make_pair("dm_command_exitControl", &SAL_dm::ackCommand_exitControl)}, 
    {"FAULT_ACK", make_pair("dm_command_abort", &SAL_dm::ackCommand_abort)}
}; 

/* 
    AckSubscriber listens to messages returned from DMCS and acks those messages back to OCS.
*/					
AckSubscriber::AckSubscriber() { 
    Node config = LoadFile("OCSDeviceCfg.yaml"); 

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

/* destructor for AckSubscriber */ 
AckSubscriber::~AckSubscriber() { 
}

/* 
    set up rabbitmq consumer to consume messages from DMCS. 
*/  
void AckSubscriber::setup_consumer() { 
    try {
	object pyimport = import("Consumer");
	ocs_consumer = pyimport.attr("Consumer")(base_broker_addr, OCS_CONSUME);  
    }
    catch (error_already_set const &){ 
	PyErr_Print();
    }
}

/* 
    constructs callback python function and start IOLoop when called. 
*/
void AckSubscriber::run() { 
    cout << "============> running CONSUMER <=============" << endl; 
    try { 
	object pymethod = make_function(AckSubscriber::on_dmcs_message);  
	ocs_consumer.attr("run")(pymethod); 
    }
    catch (error_already_set const &) {
	PyErr_Print();
    }
} 

/* 
    callback method using the signature defined by rabbitmq to consume messages
    :param ch: boost python rabbitmq channel object
    :param method: boost python rabbitmq method object
    :param properties: boost python rabbitmq properties object
    :param body: boost python dictionary object
*/
void AckSubscriber::on_dmcs_message(object ch, object method, object properties, dict body) { 
    string message_type, message_value;
    int cmdId;  
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
	    if (key == "CMD_ID") { 
		cmdId = stoi(value); 	
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
	(mgr.*action)(cmdId, SAL__CMD_COMPLETE, 0, "Done: OK");     
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
