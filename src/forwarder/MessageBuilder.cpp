#include <yaml-cpp/yaml.h>
#include "forwarder/MessageBuilder.h"

using namespace std;
using namespace YAML;

const char* MessageBuilder::build_ack(const string& msg_type, const string& component, const string& ack_id, const string& ack_bool) { 
    Emitter msg; 
    msg << BeginMap; 
    msg << Key << "MSG_TYPE" << Value << msg_type << "_ACK"; 
    msg << Key << "COMPONENT" << Value << component; 
    msg << Key << "ACK_ID" << Value << ack_id; 
    msg << Key << "ACK_BOOL" << Value << ack_bool; 
    msg << EndMap; 
    return msg.c_str();
}
