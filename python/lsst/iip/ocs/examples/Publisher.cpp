#include <iostream> 
#include <sstream> 
#include "SimplePublisher.h"

using namespace std; 

void send_message() { 
    string url = "amqp://OCS:OCS@141.142.208.160/%2fbunny"; 
    SimplePublisher *publisher = new SimplePublisher(url);  

    string message_type = "DO_SOMETHING"; 
    string device = "AR"; 
    string checkbox = "false"; 

    ostringstream message; 
    message << "{ MSG_TYPE: " << message_type
            << ", DEVICE: " << device 
            << ", APPLIED: true" 
            << ", CHECKBOX: " << checkbox << "}"; 

    string publish_q = "ocs_dmcs_consume"; 
    publisher->publish_message(publish_q, message.str()); 
    cout << "[x] Message sent." << endl; 
} 

int main() { 
    send_message(); 
    return 0; 
} 
