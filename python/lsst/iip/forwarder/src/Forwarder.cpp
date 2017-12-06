#include <iostream>
#include <sstream>
#include <pthread.h>
#include <yaml-cpp/yaml.h>
#include "Consumer_impl.h"
#include "SimplePublisher.h"

using namespace std;
using namespace YAML;

class Forwarder {
    public:
    //General Forwarder consumers
    Consumer *from_foreman_consumer;
    Consumer *from_fetch_consumer;
    Consumer *from_format_consumer;
    Consumer *from_forward_consumer;

    //Consumers in work threads
    Consumer *from_forwarder_to_fetch;
    Consumer *from_forwarder_to_format;
    Consumer *from_forwarder_to_forward;

    //Publishers
    SimplePublisher *FWDR_pub;
    SimplePublisher *FWDR_to_fetch_pub;
    SimplePublisher *FWDR_to_format_pub;
    SimplePublisher *FWDR_to_forward_pub;
    SimplePublisher *fetch_pub;
    SimplePublisher *fmt_pub;
    SimplePublisher *fwd_pub;
    
    string USER, PASSWD, BASE_BROKER_ADDR, FQN, HOSTNAME, IP_ADDR, CONSUME_QUEUE, USER_FORWARD_PUB, PASSWD_FORWARD_PUB;;
    string USER_PUB, PASSWD_PUB, USER_FETCH_PUB, PASSWD_FETCH_PUB, USER_FORMAT_PUB, PASSWD_FORMAT_PUB;
    string FETCH_USER, FETCH_USER_PASSWD, FORMAT_USER, FORMAT_USER_PASSWD,  FORWARD_USER, FORWARD_USER_PASSWD;
    string FETCH_USER_PUB, FETCH_USER_PUB_PASSWD, FORMAT_USER_PUB, FORMAT_USER_PUB_PASSWD; 
    string FORWARD_USER_PUB, FORMAT_USER_PUB_PASSWD;

    Forwarder();
    ~Forwarder();
    void setup_consumers(string);
    void on_foreman_message(string body);
    void on_fetch_message(string body);
    void on_format_message(string body);
    void on_forward_message(string body);

    void on_forwarder_to_fetch_message(string body);
    void on_forwarder_to_format_message(string body);
    void on_forwarder_to_forward_message(string body);

    void process_new_visit(Node n);
    void process_health_check(Node n);
    void process_take_image(Node n);
    void process_end_readout(Node n);

    void process_fetch(Node n);
    void process_fetch_ack(Node n);
    void process_fetch_health_check(Node n);
    void process_format_health_check_ack(Node n);
    void process_format(Node n);
    void process_format_ack(Node n);
    void process_format_health_check(Node n);
    void process_format_health_chech_ack(Node n);
    void process_forward(Node n);
    void process_forward_ack(Node n);

    void run();
    statis void *run_thread(void *);
};

using funcptr = void(Forwarder::*)(Node);

//Primary Forwarder message actions
map<string, funcptr> on_foreman_message_actions = {
    { "AR_NEW_VISIT", &Forwarder::process_new_visit},
    { "PP_NEW_VISIT", &Forwarder::process_new_visit},
    { "SP_NEW_VISIT", &Forwarder::process_new_visit},
    { "AR_FWDR_HEALTH_CHECK", &Forwarder::process_health_check},
    { "PP_FWDR_HEALTH_CHECK", &Forwarder::process_health_check},
    { "SP_FWDR_HEALTH_CHECK", &Forwarder::process_health_check},
    { "AR_TAKE_IMAGE", &Forwarder::process_take_image},
    { "PP_TAKE_IMAGE", &Forwarder::process_take_image},
    { "SP_TAKE_IMAGE", &Forwarder::process_take_image},
    { "AR_END_READOUT", &Forwarder::process_end_readout},
    { "PP_END_READOUT", &process_end_readout},
    { "SP_END_READOUT", &process_end_readout}
};

//The next three handlers are essentially acks...
map<string, funcptr> on_fetch_message_actions = {
    { "FETCH_HEALTH_CHECK_ACK", &Forwarder::process_fetch_health_check_ack},
    { "AR_FETCH_ACK", &Forwarder::process_fetch_ack},
    { "PP_FETCH_ACK", &Forwarder::process_fetch_ack],
    { "SP_FETCH_ACK", &Forwarder::process_fetch_ack]

};

map<string, funcptr> on_format_message_actions = {
    { "FORMAT_HEALTH_CHECK_ACK", &Forwarder::process_format_health_check_ack},
    { "AR_FORMAT_ACK", &Forwarder::process_format_ack},
    { "PP_FORMAT_ACK", &Forwarder::process_format_ack],
    { "SP_FORMAT_ACK", &Forwarder::process_format_ack]

};

map<string, funcptr> on_forward_message_actions = {
    { "FORWARD_HEALTH_CHECK_ACK", &Forwarder::process_forward_health_check_ack},
    { "AR_FORMAT_ACK", &Forwarder::process_forward_ack},
    { "PP_FORMAT_ACK", &Forwarder::process_forward_ack],
    { "SP_FORMAT_ACK", &Forwarder::process_forward_ack]

};


//Forwarder Component message actions
//This handler is for messages from Primary Forwarder to fetch thread
map<string, funcptr> on_forwarder_to_fetch_message_actions = {
    { "FETCH_HEALTH_CHECK", &Forwarder::process_fetch_health_check},
    { "AR_FETCH", &Forwarder::process_fetch},
    { "PP_FETCH", &Forwarder::process_fetch],
    { "SP_FETCH", &Forwarder::process_fetch]
};

//This handler is for messages from Primary Forwarder to format thread
map<string, funcptr> on_forwarder_to_format_message_actions = {
    { "FORMAT_HEALTH_CHECK", &Forwarder::process_format_health_check},
    { "AR_FORMAT", &Forwarder::process_format},
    { "PP_FORMAT", &Forwarder::process_format],
    { "SP_FORMAT", &Forwarder::process_format]
};

//This handler is for messages from Primary Forwarder to forward thread
map<string, funcptr> on_forwarder_to_forward_message_actions = {
    { "FORWARD_HEALTH_CHECK", &Forwarder::process_forward_health_check},
    { "AR_FORWARD", &Forwarder::process_forward},
    { "PP_FORWARD", &Forwarder::process_forward],
    { "SP_FORWARD", &Forwarder::process_forward]

};

Forwarder::Forwarder() {
    // Read config file
    Node config_file;
    try {
        config_file = LoadFile("../yaml/ForwarderCfg.yaml");
    }
    catch (YAML::BadFile& e) {
        // FIX better catch clause...at LEAST a log message
        cout << "Error reading ForwarderCfg.yaml file." << endl;
        exit(EXIT_FAILURE);
    }

    Node root;
    string USER, PASSWD, BASE_BROKER_ADDR, FQN, HOSTNAME, IP_ADDR, CONSUME_QUEUE;
    try {
        root = config_file["ROOT"];
        NAME = root["NAME"].as<string>();
        LOWER_NAME = root["LOWER_NAME"].as<string>();
        USER = root["USER"].as<string>();
        PASSWD = root["PASSWD"].as<string>();
        USER_PUB = root["USER_PUB"].as<string>();
        PASSWD_PUB = root["PASSWD_PUB"].as<string>();
        USER_FETCH_PUB = ["USER_FETCH_PUB"].as<string>();
        PASSWD_FETCH_PUB = ["PASSWD_FETCH_PUB"].as<string>();
        USER_FORMAT_PUB = ["USER_FORMAT_PUB"].as<string>();
        PASSWD_FORMAT_PUB = ["PASSWD_FORMAT_PUB"].as<string>();
        USER_FORWARD_PUB = ["USER_FORWARD_PUB"].as<string>();
        PASSWD_FORWARD_PUB = ["PASSWD_FORWARD_PUB"].as<string>();
        BASE_BROKER_ADDR = root["BASE_BROKER_ADDR"].as<string>(); // @xxx.xxx.xxx.xxx:5672/%2fbunny
        FQN = root["FQN"].as<string>();
        HOSTNAME = root["HOSTNAME"].as<string>();
        IP_ADDR = root["IP_ADDR"].as<string>();
        CONSUME_QUEUE = root["CONSUME_QUEUE"].as<string>();
        FETCH_USER = root["FETCH_USER"].as<string>();
        FETCH_USER_PASSWD = root["FETCH_USER_PASSWD"].as<string>();
        FETCH_USER_PUB = root["FETCH_USER_PUB"].as<string>();
        FETCH_USER_PUB_PASSWD = root["FETCH_USER_PUB_PASSWD"].as<string>();

        FORMAT_USER = root["FORMAT_USER"].as<string>();
        FORMAT_USER_PASSWD = root["FORMAT_USER_PASSWD"].as<string>();
        FORMAT_USER_PUB = root["FORMAT_USER_PUB"].as<string>();
        FORMAT_USER_PUB_PASSWD = root["FORMAT_USER_PUB_PASSWD"].as<string>();

        FORWARD_USER = root["FORWARD_USER"].as<string>();
        FORWARD_USER_PASSWD = root["FORWARD_USER_PASSWD"].as<string>();
        FORWARD_USER_PUB = root["FORWARD_USER_PUB"].as<string>();
        FORWARD_USER_PUB_PASSWD = root["FORWARD_USER_PUB_PASSWD"].as<string>();
    }
    catch (YAML::TypedBadConversion<string>& e) {
        cout << "ERROR: In ForwarderCfg.yaml, cannot read required elements from this file." << endl;
    }

    //ostringstream full_broker_url;
    //full_broker_url << "amqp://" << user_name << ":" << passwd << basePbroker_addr from above...

    setup_consumers(BASE_BROKER_ADDR);
    setup_publishers(BASE_BROKER_ADDR);
    
}

void Forwarder::setup_consumers(string BASE_BROKER_ADDR){
    //Consumers for Primary Forwarder
    ostringstream full_broker_url;
    full_broker_url << "amqp://" << USER << ":" << PASSWD << BASE_BROKER_ADDR ;
    from_foreman_consumer = new Consumer(full_broker_url, CONSUME_QUEUE);

    ostringstream consume_queue;
    consume_queue << CONSUME_QUEUE << "_from_fetch";
    from_fetch_consumer = new Consumer(full_broker_url, consume_queue);

    ostringstream consume_queue;
    consume_queue << CONSUME_QUEUE << "_from_format";
    from_format_consumer = new Consumer(full_broker_url, consume_queue);

    ostringstream consume_queue;
    consume_queue << CONSUME_QUEUE << "_from_forward";
    from_forward_consumer = new Consumer(full_broker_url, consume_queue);

    //Consumers for sub-components
    ostringstream consume_queue;

    ostringstream full_broker_url;
    ostringstream consume_queue;
    full_broker_url << "amqp://" << FETCH_USER << ":" << FETCH_USER_PASSWD << BASE_BROKER_ADDR ;
    consume_queue << "fetch_consume_from_" << LOWER_NAME;
    from_forwarder_to_fetch = new Consumer(full_broker_url, consume_queue);

    ostringstream full_broker_url;
    ostringstream consume_queue;
    full_broker_url << "amqp://" << FORMAT_USER << ":" << FORMAT_USER_PASSWD << BASE_BROKER_ADDR ;
    consume_queue << "format_consume_from_" << LOWER_NAME;
    from_forwarder_to_format = new Consumer(full_broker_url, consume_queue);

    ostringstream full_broker_url;
    ostringstream consume_queue;
    full_broker_url << "amqp://" << FORWARD_USER << ":" << FORWARD_USER_PASSWD << BASE_BROKER_ADDR ;
    consume_queue << "forward_consume_from_" << LOWER_NAME;
    from_forwarder_to_forward = new Consumer(full_broker_url, consume_queue);

}

void Forwarder::setup_publishers(string BASE_BROKER_ADDR){
    //Publishers
    ostringstream full_broker_url;
    full_broker_url << "amqp://" << USER_PUB << ":" << PASSWD_PUB << BASE_BROKER_ADDR;
    FWDR_pub = new SimplePublisher(full_broker_url);

    ostringstream full_broker_url;
    full_broker_url << "amqp://" << USER_FETCH_PUB << ":" << PASSWD_FETCH_PUB << BASE_BROKER_ADDR;
    FWDR_to_fetch_pub - new SimplePublisher(full_broker_url);

    ostringstream full_broker_url;
    full_broker_url << "amqp://" << USER_FORMAT_PUB << ":" << PASSWD_FORMAT_PUB << BASE_BROKER_ADDR;
    FWDR_to_format_pub = new SimplePublisher(full_broker_url);

    ostringstream full_broker_url;
    full_broker_url << "amqp://" << USER_FORWARD_PUB << ":" << PASSWD_FORWARD_PUB << BASE_BROKER_ADDR;
    FWDR_to_forward_pub = new SimplePublisher(full_broker_url);

    ostringstream full_broker_url;
    full_broker_url << "amqp://" << FETCH_USER_PUB << ":" << FETCH_USER_PUB_PASSWD << BASE_BROKER_ADDR;
    fetch_pub = new SimplePublisher(full_broker_url);

    ostringstream full_broker_url;
    full_broker_url << "amqp://" << FORMAT_USER_PUB << ":" << FORMAT_USER_PUB_PASSWD << BASE_BROKER_ADDR;
    fmt_pub = new SimplePublisher(full_broker_url);

    ostringstream full_broker_url;
    full_broker_url << "amqp://" << FORWARD_USER_PUB << ":" << FORWARD_USER_PUB_PASSWD << BASE_BROKER_ADDR;
    fwd_pub = new SimplePublisher(full_broker_url);

}



//Messages received by Primary Forwarder from Foreman
void Forwarder::on_foreman_message(string body) {
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_foreman_message_actions[message_type];
    (this->*action)(node);
}

//Messages received by Primary Forwarder from fetch thread
void Forwarder::on_fetch_message(string body) {
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_fetch_message_actions[message_type];
    (this->*action)(node);
}

//Messages received by Primary Forwarder from format thread
void Forwarder::on_format_message(string body) {
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_format_message_actions[message_type];
    (this->*action)(node);
}

//Messages received by Primary Forwarder from forwardthread
void Forwarder::on_forward_message(string body) {
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_forward_message_actions[message_type];
    (this->*action)(node);
}



//Messages received by the fetch, format, and forward threads
void Forwarder::on_forwarder_to_fetch_message(string body) {
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_forward_to_fetch_message_actions[message_type];
    (this->*action)(node);
}

void Forwarder::on_forwarder_to_format_message(string body) {
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_forwarder_to format_message_actions[message_type];
    (this->*action)(node);
}

void Forwarder::on_forwarder_to_forward_message(string body) {
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_forwarder_to_forward_message_actions[message_type];
    (this->*action)(node);
}


//Message action handler methods...
void Forwarder::process_new_visit(Node n) {
    return;
}

void Forwarder::process_health_check(Node n) {
    return;
}

void Forwarder::process_take_image(Node n) {
    return;
}

void Forwarder::process_end_readout(Node n) {
    return;
}

void Forwarder::process_fetch(Node n) {
    return;
}

void Forwarder::process_fetch_ack(Node n) {
    return;
}

void Forwarder::process_fetch_health_check(Node n) {
    return;
}

void Forwarder::process_fetch_health_check_ack(Node n) {
    return;
}

void Forwarder::process_format(Node n) {
    return;
}

void Forwarder::process_format_ack(Node n) {
    return;
}

void Forwarder::process_format_health_check(Node n) {
    return;
}

void Forwarder::process_format_health_check_ack(Node n) {
    return;
}

void Forwarder::process_forward(Node n) {
    return;
}

void Forwarder::process_forward_ack(Node n) {
    return;
}

void Forwarder::process_forward_health_check(Node n) {
    return;
}

void Forwarder::process_forward_health_check_ack(Node n) {
    return;
}






