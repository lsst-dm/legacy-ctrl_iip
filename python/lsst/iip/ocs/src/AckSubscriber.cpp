#include <string.h>
#include <iostream> 
#include <yaml-cpp/yaml.h>
#include "SAL_dm.h"
#include "unistd.h"
#include "AckSubscriber.h"

using namespace std; 
using namespace YAML; 

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
    Node config = LoadFile("ForemanCfg.yaml"); 

    string usrname = config["ROOT"]["OCS"]["OCS_NAME"].as<string>(); 
    string passwd = config["ROOT"]["OCS"]["OCS_PASSWD"].as<string>(); 
    string addr = config["ROOT"]["BASE_BROKER_ADDR"].as<string>(); 
    ostringstream broker_addr; 
    broker_addr << "amqp://" << usrname << ":" << passwd << "@" << addr; 
    base_broker_addr = broker_addr.str(); 

    OCS_CONSUME = config["ROOT"]["OCS"]["OCS_CONSUME"].as<string>(); 

    cout << "CONFIG: " << base_broker_addr << " @ " << OCS_CONSUME << endl; 

    setup_consumer(); 
} 

/* destructor for AckSubscriber */ 
AckSubscriber::~AckSubscriber() { 
    delete ack_consumer; 
}

/* 
    set up rabbitmq consumer to consume messages from DMCS. 
*/  
void AckSubscriber::setup_consumer() { 
    ack_consumer = new Consumer(base_broker_addr, OCS_CONSUME); 
}

/* 
    constructs callback python function and start IOLoop when called. 
*/
void AckSubscriber::run() { 
    cout << "============> running CONSUMER <=============" << endl; 
    ack_consumer->run(on_message); 
} 


/* 
    callback method using the signature defined by rabbitmq to consume messages
    :param ch: boost python rabbitmq channel object
    :param method: boost python rabbitmq method object
    :param properties: boost python rabbitmq properties object
    :param body: boost python dictionary object
*/
void AckSubscriber::on_message(string message) { 
    cout << "MSG: " << message << endl; 
    string message_value; 
    int cmdId; 

    Node node = Load(message); 
    message_value = node["MSG_TYPE"].as<string>(); 
    cmdId = stoi(node["CMD_ID"].as<string>()); 
    
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
