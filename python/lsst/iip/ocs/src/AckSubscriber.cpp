#include <string.h>
#include <iostream> 
#include <yaml-cpp/yaml.h>
#include "SAL_archiver.h"
#include "SAL_catchuparchiver.h" 
#include "SAL_processingcluster.h"
#include "unistd.h"
#include "OCS_Bridge.h"
#include "AckSubscriber.h"

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
    cmdId = stoi(node["CMD_ID"].as<string>()); 
    
    SAL_archiver mgr = SAL_archiver();
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
