#include <iostream> 
#include <yaml-cpp/yaml.h> 
#include "SimplePublisher.h" 
#include "Consumer.h" 

using namespace std; 
using namespace YAML; 


class daq_tester { 
    SimplePublisher *publisher; 
    Consumer *consumer; 

    void run(); 
    void on_message(string); 
}; 

daq_tester::daq_tester() { 
    string broker_addr = "amqp://OCS:OCS@141.142.208.209:5672/%2fbunny"; 
    string queue_name = "dmcs_ocs_consume"; 
    publisher = new SimplePublisher(broker_addr); 
    consumer = new Consumer(broker_addr, queue_name); 
} 

void daq_tester::run() { 
    consumer->run(on_message); 
}

void daq_tester::on_message(string message) { 
    cout << "MESSAGE RECEIVED: " << message << endl; 
    Node node = Load(message); 
    string msg_type = node["MSG_TYPE"].as<string>();

    ostringstream message; 
    message << "{ MSG_TYPE: HELLO }";  
    publisher->publish_message("ocs_dmcs_publish", message.str()); 
} 


int main() { 
    daq_tester tester; 
    tester.run(); 
    return 0; 
} 
