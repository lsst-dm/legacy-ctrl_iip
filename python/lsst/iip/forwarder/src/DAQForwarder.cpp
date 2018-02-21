/////////////////////////////////////////////////////////////////
//

#include <sys/stat.h> 
#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <vector> 
#include <algorithm> 
#include <iostream>
#include <sstream>
#include <pthread.h>
#include <fstream>
#include <yaml-cpp/yaml.h>
#include "Consumer_impl.h"
#include "SimplePublisher.h"
#include "fitsio.h"

#include "daq/Location.hh"
#include "daq/LocationSet.hh"

#include "ims/Store.hh"
#include "ims/Image.hh"
#include "ims/Source.hh"
#include "ims/Slice.hh"
#include "ims/Science.hh"


#define SECONDARY_HDU 2
#define HEIGHT 512
#define WIDTH 2048
#define N_AMPS 16

using namespace std;
using namespace YAML;

class Forwarder {
    public:

    //Important 'per readout' values
    std::vector<string> visit_raft_list;
    std::vector<std::vector<string>> visit_ccd_list_by_raft;
    std::vector<string> image_id_list;

    std::vector<string> current_image_work_list;
    std::vector<string> finished_image_work_list;
    std::vector<string> files_transferred_list;
    std::vector<string> checksum_list;

    std::string Session_ID = "";
    std::string Visit_ID = "";
    std::string Job_Num = "";
    std::string Target_Location = "";
    std::string Daq_Addr = "";
    std::string Work_Dir = ""; 
    std::string Src_Dir = ""; 
    std::string Name = ""; //such as FORWARDER_1
    std::string Lower_Name; //such as f1
    std::string Component = ""; //such as FORWARDER_1
    int Num_Images = 0; 
   
    
    std::string consume_queue = "";
    std::string fetch_consume_queue = "";
    std::string format_consume_queue = "";
    std::string forward_consume_queue = "";

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
    
    string USER, PASSWD, BASE_BROKER_ADDR, FQN, HOSTNAME, IP_ADDR, CONSUME_QUEUE, USER_FORWARD_PUB, PASSWD_FORWARD_PUB;
    string USER_PUB, PASSWD_PUB, USER_FETCH_PUB, PASSWD_FETCH_PUB, USER_FORMAT_PUB, PASSWD_FORMAT_PUB;
    string FETCH_USER, FETCH_USER_PASSWD, FORMAT_USER, FORMAT_USER_PASSWD,  FORWARD_USER, FORWARD_USER_PASSWD;
    string FETCH_USER_PUB, FETCH_USER_PUB_PASSWD, FORMAT_USER_PUB, FORMAT_USER_PUB_PASSWD; 
    string FORWARD_USER_PUB, FORWARD_USER_PUB_PASSWD;

    vector<string> readout_img_ids; 
    map<string, string> header_info_dict; 
    map<string, string> take_img_done_msg; 

    Forwarder();
    ~Forwarder();
    void setup_consumers(string);
    void setup_publishers(string); 

    //Declarations for message callbacks
    void on_foreman_message(string body);
    void on_fetch_message(string body);
    void on_format_message(string body);
    void on_forward_message(string body);

    void on_forwarder_to_fetch_message(string body);
    void on_forwarder_to_format_message(string body);
    void on_forwarder_to_forward_message(string body);

    //Declarations message handlers within callbacks
    void process_new_visit(Node n);
    void process_health_check(Node n);
    void process_xfer_params(Node n);
    void process_take_images(Node n);
    void process_take_images_done(Node n);
    void process_end_readout(Node n);
    void process_header_ready(Node n); 

    void process_fetch(Node n);
    void process_fetch_ack(Node n);
    void process_fetch_end_readout(Node n);
    void process_fetch_health_check(Node n);
    void process_fetch_health_check_ack(Node n);
    void process_format(Node n);
    void process_format_ack(Node n);
    void process_format_health_check(Node n);
    void process_format_health_check_ack(Node n);
    void process_forward(Node n);
    void process_forward_ack(Node n);
    void process_forward_health_check(Node n);
    void process_forward_health_check_ack(Node n);

    void run();
    static void *run_thread(void *);

    void fetch_readout_image(string image_id, string dir_prefix);
    void fetch_readout_raft(string raft, vector<string> ccd_list, string image_id, string dir_prefix);
    void fetch_reassemble_raft_image(string raft, map<string, vector<string>> source_boards, string image_id, string dir_prefix);
    void fetch_reassemble_process(string raft, string image_id, const DAQ::Location& location, const IMS::Image& image, std::vector<string> ccds_for_board, string dir_prefix);
    void fetch_set_up_filehandles(std::vector<std::ofstream> &fh_set, string image_id, string raft, string ccd, string dir_prefix);
    void fetch_close_filehandles(std::vector<std::ofstream> &fh_set);

    char* format_read_img_segment(const char*);
    unsigned char** format_assemble_pixels(char *);
    void format_write_img(std::string, std::string);
    void format_assemble_img(Node);
    void format_send_completed_msg(std::string);
    void format_look_for_work(); 
    void format_process_end_readout(Node); 
    void format_get_header(Node); 
    vector<string> format_list_files(string); 

    void forward_process_end_readout(Node); 
    void forward_process_take_images_done(Node); 
};

using funcptr = void(Forwarder::*)(Node);

struct arg_struct {
    Consumer *consumer;
    Forwarder *forwarder;
    callback<Forwarder> funcptr;
};

//Primary Forwarder message actions
map<string, funcptr> on_foreman_message_actions = {
    { "AR_NEW_VISIT", &Forwarder::process_new_visit},
    { "PP_NEW_VISIT", &Forwarder::process_new_visit},
    { "SP_NEW_VISIT", &Forwarder::process_new_visit},
    { "AR_FWDR_HEALTH_CHECK", &Forwarder::process_health_check},
    { "PP_FWDR_HEALTH_CHECK", &Forwarder::process_health_check},
    { "SP_FWDR_HEALTH_CHECK", &Forwarder::process_health_check},
    { "AR_FWDR_XFER_PARAMS", &Forwarder::process_xfer_params},
    { "PP_FWDR_XFER_PARAMS", &Forwarder::process_xfer_params},
    { "SP_FWDR_XFER_PARAMS", &Forwarder::process_xfer_params},
    { "AR_FWDR_TAKE_IMAGES", &Forwarder::process_take_images},
    { "PP_TAKE_IMAGES", &Forwarder::process_take_images},
    { "SP_TAKE_IMAGES", &Forwarder::process_take_images},
    { "AR_FWDR_END_READOUT", &Forwarder::process_end_readout},
    { "PP_END_READOUT", &Forwarder::process_end_readout},
    { "SP_END_READOUT", &Forwarder::process_end_readout},
    { "AR_TAKE_IMAGES_DONE", &Forwarder::process_take_images_done},
    { "PP_TAKE_IMAGES_DONE", &Forwarder::process_take_images_done},
    { "SP_TAKE_IMAGES_DONE", &Forwarder::process_take_images_done}, 
    { "HEADER_READY", &Forwarder::process_header_ready }, 
};

//The next three handlers are essentially acks...
map<string, funcptr> on_fetch_message_actions = {
    { "FETCH_HEALTH_CHECK_ACK", &Forwarder::process_fetch_health_check_ack},
    { "AR_FETCH_ACK", &Forwarder::process_fetch_ack},
    { "PP_FETCH_ACK", &Forwarder::process_fetch_ack},
    { "SP_FETCH_ACK", &Forwarder::process_fetch_ack}

};

map<string, funcptr> on_format_message_actions = {
    { "FORMAT_HEALTH_CHECK_ACK", &Forwarder::process_format_health_check_ack},
    { "AR_FORMAT_ACK", &Forwarder::process_format_ack},
    { "PP_FORMAT_ACK", &Forwarder::process_format_ack},
    { "SP_FORMAT_ACK", &Forwarder::process_format_ack}

};

map<string, funcptr> on_forward_message_actions = {
    { "FORWARD_HEALTH_CHECK_ACK", &Forwarder::process_forward_health_check_ack},
    { "AR_FORWARD_ACK", &Forwarder::process_forward_ack},
    { "PP_FORWARD_ACK", &Forwarder::process_forward_ack},
    { "SP_FORWARD_ACK", &Forwarder::process_forward_ack}

};


//Forwarder Component message actions
//This handler is for messages from Primary Forwarder to fetch thread
map<string, funcptr> on_forwarder_to_fetch_message_actions = {
    { "FETCH_HEALTH_CHECK", &Forwarder::process_fetch_health_check},
    { "FETCH_END_READOUT", &Forwarder::process_fetch},
    { "FETCH_TAKE_IMAGES_DONE", &Forwarder::process_fetch},
    { "AR_FETCH", &Forwarder::process_fetch},
    { "PP_FETCH", &Forwarder::process_fetch},
    { "SP_FETCH", &Forwarder::process_fetch}
};

//This handler is for messages from Primary Forwarder to format thread
map<string, funcptr> on_forwarder_to_format_message_actions = {
    { "FORMAT_HEALTH_CHECK", &Forwarder::process_format_health_check},
    { "AR_FORMAT", &Forwarder::process_format},
    { "PP_FORMAT", &Forwarder::process_format},
    { "SP_FORMAT", &Forwarder::process_format}, 
    { "FORMAT_END_READOUT", &Forwarder::format_process_end_readout}, 
    { "FORMAT_HEADER_READY", &Forwarder::format_get_header}, 
    { "FORMAT_TAKE_IMAGES_DONE", &Forwarder::process_format},
};

//This handler is for messages from Primary Forwarder to forward thread
map<string, funcptr> on_forwarder_to_forward_message_actions = {
    { "FORWARD_HEALTH_CHECK", &Forwarder::process_forward_health_check},
    { "AR_FORWARD", &Forwarder::process_forward},
    { "TAKE_IMAGES_DONE", &Forwarder::process_forward},
    { "PP_FORWARD", &Forwarder::process_forward},
    { "SP_FORWARD", &Forwarder::process_forward}, 
    { "FORWARD_END_READOUT", &Forwarder::forward_process_end_readout}, 
    { "FORWARD_TAKE_IMAGES_DONE", &Forwarder::forward_process_take_images_done},  
};

map<string, int> Board_Layout = {
    { "00", 0},
    { "10", 0},
    { "20", 0},
    { "01", 1},
    { "11", 1},
    { "21", 1},
    { "02", 2},
    { "12", 2},
    { "22", 2}

};

map<string, vector<string>> All_Boards = {
    { "0", {"00","10","20"}},
    { "1", {"01","11","21"}},
    { "2", {"02","12","22"}}

};

Forwarder::Forwarder() {
    // Read config file
    Node config_file;
    try {
        config_file = LoadFile("./ForwarderCfg.yaml");
    }
    catch (YAML::BadFile& e) {
        // FIX better catch clause...at LEAST a log message
        cout << "Error reading ForwarderCfg.yaml file." << endl;
        exit(EXIT_FAILURE);
    }

    Node root;
    string NAME, BASE_BROKER_ADDR, FQN, HOSTNAME, IP_ADDR;
    try {
        root = config_file["ROOT"];
        this->Name = root["NAME"].as<string>();
        this->Component = root["FQN"].as<string>();
        this->Lower_Name = root["LOWER_NAME"].as<string>();
        USER = root["USER"].as<string>();
        PASSWD = root["PASSWD"].as<string>();
        USER_PUB = root["USER_PUB"].as<string>();
        PASSWD_PUB = root["PASSWD_PUB"].as<string>();
        USER_FETCH_PUB = root["USER_FETCH_PUB"].as<string>();
        PASSWD_FETCH_PUB = root["PASSWD_FETCH_PUB"].as<string>();
        USER_FORMAT_PUB = root["USER_FORMAT_PUB"].as<string>();
        PASSWD_FORMAT_PUB = root["PASSWD_FORMAT_PUB"].as<string>();
        USER_FORWARD_PUB = root["USER_FORWARD_PUB"].as<string>();
        PASSWD_FORWARD_PUB = root["PASSWD_FORWARD_PUB"].as<string>();
        this->BASE_BROKER_ADDR = root["BASE_BROKER_ADDR"].as<string>(); // @xxx.xxx.xxx.xxx:5672/%2fbunny
        HOSTNAME = root["HOSTNAME"].as<string>();
        IP_ADDR = root["IP_ADDR"].as<string>();
        this->Work_Dir = root["WORK_DIR"].as<string>();
        this->Src_Dir = root["SRC_DIR"].as<string>(); 
        this->consume_queue = root["CONSUME_QUEUE"].as<string>();
        this->fetch_consume_queue = root["FETCH_CONSUME_QUEUE"].as<string>();
        this->format_consume_queue = root["FORMAT_CONSUME_QUEUE"].as<string>();
        this->forward_consume_queue = root["FORWARD_CONSUME_QUEUE"].as<string>();
        this->FETCH_USER = root["FETCH_USER"].as<string>();
        this->FETCH_USER_PASSWD = root["FETCH_USER_PASSWD"].as<string>();
        this->FETCH_USER_PUB = root["FETCH_USER_PUB"].as<string>();
        this->FETCH_USER_PUB_PASSWD = root["FETCH_USER_PUB_PASSWD"].as<string>();

        this->FORMAT_USER = root["FORMAT_USER"].as<string>();
        this->FORMAT_USER_PASSWD = root["FORMAT_USER_PASSWD"].as<string>();
        this->FORMAT_USER_PUB = root["FORMAT_USER_PUB"].as<string>();
        this->FORMAT_USER_PUB_PASSWD = root["FORMAT_USER_PUB_PASSWD"].as<string>();

        this->FORWARD_USER = root["FORWARD_USER"].as<string>();
        this->FORWARD_USER_PASSWD = root["FORWARD_USER_PASSWD"].as<string>();
        this->FORWARD_USER_PUB = root["FORWARD_USER_PUB"].as<string>();
        this->FORWARD_USER_PUB_PASSWD = root["FORWARD_USER_PUB_PASSWD"].as<string>();
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
    full_broker_url << "amqp://" << this->USER << ":" << this->PASSWD << this->BASE_BROKER_ADDR ;
    cout << full_broker_url.str() << endl;
    from_foreman_consumer = new Consumer(full_broker_url.str(), this->consume_queue);

    ostringstream consume_queue1;
    consume_queue1 << this->consume_queue << "_from_fetch";
    cout << full_broker_url.str() << endl;
    from_fetch_consumer = new Consumer(full_broker_url.str(), consume_queue1.str());

    ostringstream consume_queue2;
    consume_queue2 << this->consume_queue << "_from_format";
    cout << full_broker_url.str() << endl;
    from_format_consumer = new Consumer(full_broker_url.str(), consume_queue2.str());

    ostringstream consume_queue3;
    consume_queue3 << this->consume_queue << "_from_forward";
    ostringstream from_fwd_broker_url;
    from_fwd_broker_url << "amqp://" << this->USER << ":" << this->PASSWD << this->BASE_BROKER_ADDR ;
    cout << from_fwd_broker_url.str() << endl;
    from_forward_consumer = new Consumer(full_broker_url.str(), consume_queue3.str());

    //Consumers for sub-components
    //ostringstream consume_queue;

    ostringstream full_broker_url2;
    full_broker_url2 << "amqp://" << this->FETCH_USER << ":" << this->FETCH_USER_PASSWD << this->BASE_BROKER_ADDR ;
    cout << full_broker_url.str() << endl;
    from_forwarder_to_fetch = new Consumer(full_broker_url.str(), this->fetch_consume_queue);

    ostringstream full_broker_url3;
    full_broker_url3 << "amqp://" << this->FORMAT_USER << ":" << this->FORMAT_USER_PASSWD << this->BASE_BROKER_ADDR;
    cout << full_broker_url3.str() << endl;
    from_forwarder_to_format = new Consumer(full_broker_url.str(), this->format_consume_queue);
    //cout << this->format_consume_queue << endl; 

    ostringstream full_broker_url4;
    full_broker_url4 << "amqp://" << this->FORWARD_USER << ":" << this->FORWARD_USER_PASSWD << this->BASE_BROKER_ADDR ;
    cout << full_broker_url4.str() << endl;
    from_forwarder_to_forward = new Consumer(full_broker_url.str(), this->forward_consume_queue);

}

void Forwarder::run() {
    //Set up argument structs for all seven consumer threads
    //Primary Forwarder consumer threads
    arg_struct *args1 = new arg_struct;
    args1->consumer = from_foreman_consumer;
    args1->forwarder = this;
    args1->funcptr = &Forwarder::on_foreman_message;

    arg_struct *args2 = new arg_struct;
    args2->consumer = from_fetch_consumer;
    args2->forwarder = this;
    args2->funcptr = &Forwarder::on_fetch_message;

    arg_struct *args3 = new arg_struct;
    args3->consumer = from_format_consumer;
    args3->forwarder = this;
    args3->funcptr = &Forwarder::on_format_message;

    arg_struct *args4 = new arg_struct;
    args4->consumer = from_forward_consumer;
    args4->forwarder = this;
    args4->funcptr = &Forwarder::on_forward_message;

    //Subcomponent consumer threads
    arg_struct *args5 = new arg_struct;
    args5->consumer = from_forwarder_to_fetch;
    args5->forwarder = this;
    args5->funcptr = &Forwarder::on_forwarder_to_fetch_message;

    arg_struct *args6 = new arg_struct;
    args6->consumer = from_forwarder_to_format;
    args6->forwarder = this;
    args6->funcptr = &Forwarder::on_forwarder_to_format_message;

    arg_struct *args7 = new arg_struct;
    args7->consumer = from_forwarder_to_forward;
    args7->forwarder = this;
    args7->funcptr = &Forwarder::on_forwarder_to_forward_message;

    //Create then run threads
    pthread_t t1;
    pthread_create(&t1, NULL, &Forwarder::run_thread, args1);

    pthread_t t2;
    pthread_create(&t2, NULL, &Forwarder::run_thread, args2);

    pthread_t t3;
    pthread_create(&t3, NULL, &Forwarder::run_thread, args3);

    pthread_t t4;
    pthread_create(&t4, NULL, &Forwarder::run_thread, args4);

    pthread_t t5;
    pthread_create(&t5, NULL, &Forwarder::run_thread, args5);

    pthread_t t6;
    pthread_create(&t6, NULL, &Forwarder::run_thread, args6);

    pthread_t t7;
    pthread_create(&t7, NULL, &Forwarder::run_thread, args7);

}

void *Forwarder::run_thread(void *pargs) {

    arg_struct *params = ((arg_struct *) pargs);
    Consumer *consumer = params->consumer;
    Forwarder *forwarder = params->forwarder;
    callback<Forwarder> on_msg = params->funcptr;

    consumer->run<Forwarder>(forwarder, on_msg);
}


void Forwarder::setup_publishers(string BASE_BROKER_ADDR){
    //Publishers
    ostringstream full_broker_url;
    full_broker_url << "amqp://" << this->USER_PUB << ":" << this->PASSWD_PUB << this->BASE_BROKER_ADDR;
    cout << "Pub Broker url is: " << full_broker_url.str() << endl;
    FWDR_pub = new SimplePublisher(full_broker_url.str());

    ostringstream full_broker_url1;
    full_broker_url1 << "amqp://" << this->USER_FETCH_PUB << ":" << this->PASSWD_FETCH_PUB << this->BASE_BROKER_ADDR;
    cout << "Pub Broker url is: " << full_broker_url1.str() << endl;
    FWDR_to_fetch_pub = new SimplePublisher(full_broker_url1.str());

    ostringstream full_broker_url2;
    full_broker_url2 << "amqp://" << this->USER_FORMAT_PUB << ":" << this->PASSWD_FORMAT_PUB << this->BASE_BROKER_ADDR;
    cout << "Pub Broker url is: " << full_broker_url2.str() << endl;
    FWDR_to_format_pub = new SimplePublisher(full_broker_url2.str());

    ostringstream full_broker_url3;
    full_broker_url3 << "amqp://" << this->USER_FORWARD_PUB << ":" << this->PASSWD_FORWARD_PUB << this->BASE_BROKER_ADDR;
    cout << "Pub Broker url is: " << full_broker_url3.str() << endl;
    FWDR_to_forward_pub = new SimplePublisher(full_broker_url3.str());

    ostringstream full_broker_url4;
    full_broker_url4 << "amqp://" << this->FETCH_USER_PUB << ":" << this->FETCH_USER_PUB_PASSWD << this->BASE_BROKER_ADDR;
    cout << "Pub Broker url is: " << full_broker_url4.str() << endl;
    fetch_pub = new SimplePublisher(full_broker_url4.str());

    ostringstream full_broker_url5;
    full_broker_url5 << "amqp://" << this->FORMAT_USER_PUB << ":" << this->FORMAT_USER_PUB_PASSWD << this->BASE_BROKER_ADDR;
    cout << "Pub Broker url is: " << full_broker_url5.str() << endl;
    fmt_pub = new SimplePublisher(full_broker_url5.str());

    ostringstream full_broker_url6;
    full_broker_url6 << "amqp://" << this->FORWARD_USER_PUB << ":" << this->FORWARD_USER_PUB_PASSWD << this->BASE_BROKER_ADDR;
    cout << "Pub Broker url is: " << full_broker_url6.str() << endl;
    fwd_pub = new SimplePublisher(full_broker_url6.str());
}



//Messages received by Primary Forwarder from Foreman
void Forwarder::on_foreman_message(string body) {
    cout << "In forwarder callback that receives msgs from AR foreman" << endl;
    cout << "-----------Message Body Is:------------" << endl;
    cout << body << endl;
    cout << "----------------------" << endl;
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_foreman_message_actions[message_type];
    (this->*action)(node);
}

//Messages received by Primary Forwarder from fetch thread
void Forwarder::on_fetch_message(string body) {
    cout << "ON_FETCH: " << body << endl;
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_fetch_message_actions[message_type];
    (this->*action)(node);
}

//Messages received by Primary Forwarder from format thread
void Forwarder::on_format_message(string body) {
    cout << "ON_FORMAT: " << body << endl;
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_format_message_actions[message_type];
    (this->*action)(node);
}

//Messages received by Primary Forwarder from forwardthread
void Forwarder::on_forward_message(string body) {
    cout << "ON_FORWARD: " << body << endl;
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_forward_message_actions[message_type];
    (this->*action)(node);
}



//Messages received by the fetch, format, and forward threads
void Forwarder::on_forwarder_to_fetch_message(string body) {
    cout << "In fETCHr callback that receives msgs from main forwarder thread" << endl;
    cout << "-----------Message Body Is:------------" << endl;
    cout << body << endl;
    cout << "----------------------" << endl;
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_forwarder_to_fetch_message_actions[message_type];
    (this->*action)(node);
}

void Forwarder::on_forwarder_to_format_message(string body) {
    cout << "In format callback that receives msgs from main forwarder thread" << endl;
    cout << "-----------Message Body Is:------------" << endl;
    cout << body << endl;
    cout << "----------------------" << endl;
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_forwarder_to_format_message_actions[message_type];
    (this->*action)(node);
}

void Forwarder::on_forwarder_to_forward_message(string body) {
    cout << "In forward callback that receives msgs from main forwarder thread" << endl;
    cout << "-----------Message Body Is:------------" << endl;
    cout << body << endl;
    cout << "----------------------" << endl;
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_forwarder_to_forward_message_actions[message_type];
    (this->*action)(node);
}

void Forwarder::process_header_ready(Node n) { 
    cout << "[x] phr" << endl; 
    Emitter msg; 
    msg << BeginMap; 
    msg << Key << "MSG_TYPE" << Value << "FORMAT_HEADER_READY"; 
    msg << Key << "IMAGE_ID" << Value << n["IMAGE_ID"].as<string>(); 
    msg << Key << "FILENAME" << Value << n["FILENAME"].as<string>(); 
    msg << EndMap; 
    cout << "[x] msg: " << msg.c_str() << endl;

    // publish to format thread
    FWDR_to_format_pub->publish_message(this->format_consume_queue, msg.c_str()); 
} 

//Message action handler methods...
void Forwarder::process_new_visit(Node n) {
    cout << "New Visit Message" << endl;
    return;
}

void Forwarder::process_health_check(Node n) {
    string ack_id = n["ACK_ID"].as<string>();
    string reply_queue = n["REPLY_QUEUE"].as<string>();

    string message_type = "AR_FWDR_HEALTH_CHECK_ACK";
    //string component = "AR";
    string ack_bool = "True";

    ostringstream message;
    message << "{ MSG_TYPE: " << message_type
            << ", COMPONENT: " << this->Component
            << ", ACK_ID: " << ack_id
            << ", ACK_BOOL: " << ack_bool << "}";

    FWDR_pub->publish_message(reply_queue, message.str());
    cout << "Health Check request Message, ACK sent to: " << reply_queue << endl;
    return;
}

void Forwarder::process_xfer_params(Node n) {
    cout << "Entering process_xfer_params method" << endl;
    cout << "Incoming Node n is " << n <<  endl;

    Node p = n["XFER_PARAMS"];
    cout << "Sub Node p is " << p <<  endl;

    this->visit_raft_list.clear();
    this->visit_raft_list = p["RAFT_LIST"].as<vector<string>>();
    cout << "In process_xfer_params, RAFT_LIST has been ASSIGNED to class var" << endl;

    this->visit_ccd_list_by_raft.clear();
    this->visit_ccd_list_by_raft = p["RAFT_CCD_LIST"].as<std::vector<std::vector<string>>>();
    cout << "In process_xfer_params, RAFT_CCC_LIST has been ASSIGNED to class var" << endl;

    this->Session_ID = n["SESSION_ID"].as<string>();
    cout << "After setting SESSION_ID" << endl;

    this->Job_Num = n["JOB_NUM"].as<string>();
    cout << "After setting JOB_NUM" << endl;

    this->Target_Location = n["TARGET_LOCATION"].as<string>();
    cout << "After setting TARGET_LOCATION" << endl;

    string reply_queue = n["REPLY_QUEUE"].as<string>();
    cout << "After extracting REPLY_QUEUE" << endl;

    string ack_id = n["ACK_ID"].as<string>();
    cout << "After extracting ACK_ID" << endl;

    //this->Daq_Addr = n["DAQ_ADDR"].as<string>();
    //cout << "After setting DAQ_ADDR" << endl;

    //this->Visit_ID = n["VISIT_ID"].as<string>();
    //cout << "After setting VISIT_ID" << endl;

    string message_type = "AR_FWDR_XFER_PARAMS_ACK";
    //string component = "AR";
    string ack_bool = "false";

    ostringstream message;
    message << "{ MSG_TYPE: " << message_type
            << ", COMPONENT: " << this->Component
            << ", ACK_ID: " << ack_id
            << ", ACK_BOOL: " << ack_bool << "}";

    FWDR_pub->publish_message(reply_queue, message.str());
    return;
}

void Forwarder::process_take_images(Node n) {
    cout << endl << "IN process_take_images" << endl;
    this->Num_Images = n["NUM_IMAGES"].as<int>();;
    cout << "Take Image Message...should be some tasty params here" << endl;
    return;
}

void Forwarder::process_end_readout(Node n) {
    cout << "IN PROCESS_END_READOUT" << endl;
    // Send IMAGE_ID to fetch thread...use message broker queue as work queue
    //If ForwarderCfg.yaml DAQ val == 'API', draw from actual DAQ emulator,
    //else, DAQ val will equal a path where files can be found.

    //If DAQ == 'API':  pass manifold into new fetch_and_reassemble class
    string image_id = n["IMAGE_ID"].as<string>();
    image_id_list.push_back(image_id);
    string msg_type = "FETCH_END_READOUT";
    ostringstream message;
    message << "{MSG_TYPE: " << msg_type
            << ", IMAGE_ID: " << image_id << "}";
    this->FWDR_to_fetch_pub->publish_message(this->fetch_consume_queue, message.str());
    return;
}

//From forwarder main thread to fetch thread
void Forwarder::process_fetch(Node n) {
    //If message_type FETCH_END_READOUT,
    //  Make dir using image_id as name under work_dir
    //  Fetch data from DAQ or copy from local drive
    //  Send message to Format thread with image_id as msg_type FORMAT_END_READOUT
    //Else if message_type FETCH_TAKE_IMAGES_DONE,
    //  copy msg ack params and send to Format thread as msg_type FORMAT_TAKE_IMAGES_DONE

    string type_msg = n["MSG_TYPE"].as<string>();

    if (type_msg == "FETCH_TAKE_IMAGES_DONE") {
      string new_msg_type = "FORMAT_TAKE_IMAGES_DONE";
      string job_num = n["JOB_NUM"].as<string>();
      string reply_queue = n["REPLY_QUEUE"].as<string>();
      string ack_id = n["ACK_ID"].as<string>();
      ostringstream msg;
      msg << "{MSG_TYPE: " << new_msg_type
          << ", JOB_NUM: " << job_num
          << ", REPLY_QUEUE: " << reply_queue
          << ", ACK_ID: " << ack_id << "}";
      this->fetch_pub->publish_message(this->format_consume_queue, msg.str());
      return;
    }

    if (type_msg == "FETCH_END_READOUT") {
      // For raft in raft_list:
      //   send raft and associated ccd list from raft_ccd_list to fetch_readout_image()
      //   ccd_list *could* be 'all', or a subset
      //   fetch_readout_image() should determine which boards (sources) are needed to be read for ccd list
      //   The board list should be iterated through.
      //   after each board is read, the appropriate ccds on that board should be split out
      //   This could be done with map with key being board, and val being a vector of which CCDs should be pulled
      string image_id = n["IMAGE_ID"].as<string>();
      ostringstream cmd;
      ostringstream filepath;
      filepath << this->Work_Dir << "/" << image_id;
      cmd << "mkdir " << filepath.str();
      const std::string tmpstr = cmd.str();
      const char* cmdstr = tmpstr.c_str();
      system(cmdstr);


      this->fetch_readout_image(image_id, filepath.str());


      string new_msg_type = "FORMAT_END_READOUT";
      ostringstream msg;
      msg << "{MSG_TYPE: " << new_msg_type
              << ", IMAGE_ID: " << image_id << "}";
      this->fetch_pub->publish_message(this->format_consume_queue, msg.str());
      return;
    }
}

void Forwarder::process_take_images_done(Node n) {
    ostringstream msg;
    string new_msg_type = "FETCH_TAKE_IMAGES_DONE";
    string job_num = n["JOB_NUM"].as<string>();
    string ack_id = n["ACK_ID"].as<string>();
    string reply_queue = n["REPLY_QUEUE"].as<string>();
    // 1) Message fetch to pass along this message when work queue is complete
    // 2) Later, forward thread must generate report
    // 3) Send filename_list of files transferred in report
    // 4) Send checksum_list that corressponds to each file in report

    msg << "{MSG_TYPE: " << new_msg_type 
        << ", JOB_NUM: " << job_num
        << ", REPLY_QUEUE: " << reply_queue
        << ", ACK_ID: " << ack_id << "}";
    this->FWDR_to_fetch_pub->publish_message(this->fetch_consume_queue, msg.str());
}

void Forwarder::process_fetch_ack(Node n) {
    cout << "fetch ack being processed" << endl;
    return;
}

void Forwarder::process_fetch_health_check(Node n) {
    cout << "Send helth check to just fetch queue" << endl;
    return;
}

void Forwarder::process_fetch_health_check_ack(Node n) {
    cout << "Health check ack for fetch" << endl;
    return;
}

void Forwarder::process_format(Node n) {
    cout << "process_format" << endl;
    string type_msg = n["MSG_TYPE"].as<string>();
    
    if (type_msg == "FORMAT_TAKE_IMAGES_DONE") {
      string new_msg_type = "FORWARD_TAKE_IMAGES_DONE";
      string job_num = n["JOB_NUM"].as<string>();
      string reply_queue = n["REPLY_QUEUE"].as<string>();
      string ack_id = n["ACK_ID"].as<string>();
      ostringstream msg;
      msg << "{MSG_TYPE: " << new_msg_type 
          << ", JOB_NUM: " << job_num
          << ", REPLY_QUEUE: " << reply_queue
          << ", ACK_ID: " << ack_id << "}";
      this->fmt_pub->publish_message(this->forward_consume_queue, msg.str());
      return;
    }
    return;
}

void Forwarder::process_forward(Node n) { 
    cout << "processing foward message" << endl;
} 

void Forwarder::process_format_ack(Node n) {
    cout << "processing format ack message" << endl;
    return;
}

void Forwarder::process_format_health_check(Node n) {
    cout << " Health check sent to Format only" << endl;
    return;
}

void Forwarder::process_format_health_check_ack(Node n) {
    cout << "Processing format health check ack message" << endl;
    return;
}

void Forwarder::process_forward_ack(Node n) {
  cout << "Processing forward ack message" << endl;
  return;
}

void Forwarder::process_forward_health_check(Node n) {
  cout << "Processing forward health check message" << endl;
}

void Forwarder::process_forward_health_check_ack(Node n) {
  cout << "Processing forward health check ack message" << endl;
  return;
}

////////////////////////////////////////////////////////////////////////////////
// F@
////////////////////////////////////////////////////////////////////////////////

void Forwarder::format_process_end_readout(Node node) { 
    cout << "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" << endl; 
    cout << "[f] fper" << endl;
    string image_id = node["IMAGE_ID"].as<string>(); 
    this->readout_img_ids.push_back(image_id); 
    this->format_look_for_work(); 
} 

void Forwarder::format_get_header(Node node) { 
    cout << "[f] fgh" << endl; 
    string image_id = node["IMAGE_ID"].as<string>(); 
    string filename = node["FILENAME"].as<string>(); 
    cout << "[x] " << image_id << ": " << filename << endl;
    this->header_info_dict[image_id] = filename; 
    this->format_look_for_work(); 
} 

void Forwarder::format_assemble_img(Node n) {
    cout << "[f] fai" << endl; 
    string img_id = n["IMAGE_ID"].as<string>(); 
    string header = n["HEADER"].as<string>(); 
    // create dir  /mnt/ram/FITS/IMG_10
    string fits_dir = Work_Dir + "/FITS"; 
    cout << "[x] fits_dir: " << fits_dir << endl; 
    const int dir = mkdir(fits_dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR); 
    format_write_img(img_id, header);
}


char* Forwarder::format_read_img_segment(const char *file_path) { 
    fstream img_file(file_path, fstream::in | fstream::binary); 
    long len = WIDTH * HEIGHT; 
    char *buffer = new char[len]; 
    img_file.seekg(0, ios::beg); 
    img_file.read(buffer, len); 
    img_file.close();
    return buffer;
} 

unsigned char** Forwarder::format_assemble_pixels(char *buffer) { 
    unsigned char **array = new unsigned char*[HEIGHT]; 
    array[0] = (unsigned char *) malloc( WIDTH * HEIGHT * sizeof(unsigned char)); 

    for (int i = 1; i < HEIGHT; i++) { 
        array[i] = array[i-1] + WIDTH; 
    } 

    for (int j = 0; j < HEIGHT; j++) {
        for (int i = 0; i < WIDTH; i++) {
            array[j][i]= buffer[i+j]; 
        } 
    }
    return array;
} 

void Forwarder::format_write_img(string img, string header) { 
    cout << "[x] fwi" << endl;
    long len = WIDTH * HEIGHT;
    int bitpix = BYTE_IMG; 
    long naxis = 2;
    long naxes[2] = { WIDTH, HEIGHT }; 
    long fpixel = 1; 
    long nelements = len; 
    int status = 0; 
    int hdunum = 2;
    int nkeys; 
    char card[FLEN_CARD]; 
    fitsfile *iptr, *optr; 

    // /mnt/ram/IMG_31
    string img_path = Work_Dir + "/" + img;
    string header_path = header;
    string destination = Work_Dir + "/FITS/" + img + ".fits";
    cout << "[x] header: " << header_path << endl; 
    cout << "[x] destination:" << destination << endl;

    fits_open_file(&iptr, header_path.c_str(), READONLY, &status); 
    fits_create_file(&optr, destination.c_str(), &status); 
    fits_copy_hdu(iptr, optr, 0, &status); 

    vector<string> file_names = format_list_files(img_path); 
    vector<string>::iterator it; 
    for (it = file_names.begin(); it != file_names.end(); it++) { 
        string img_segment = img_path + "/" + *it; 
        char *img_buffer = format_read_img_segment(img_segment.c_str());
        unsigned char **array = format_assemble_pixels(img_buffer); 

        fits_movabs_hdu(iptr, hdunum, NULL, &status); 
        fits_create_img(optr, bitpix, naxis, naxes, &status); 
        fits_write_img(optr, TBYTE, fpixel, nelements, array[0], &status); 

        fits_get_hdrspace(iptr, &nkeys, NULL, &status); 
        for (int i = 1; i <= nkeys; i++) { 
            fits_read_record(iptr, i, card, &status); 
            fits_write_record(optr, card, &status); 
        }
        hdunum++;
    } 
    fits_close_file(iptr, &status); 
    fits_close_file(optr, &status); 

    cout << "end of fwi" << endl;
    format_send_completed_msg(img);
} 

vector<string> Forwarder::format_list_files(string path) { 
    struct dirent *entry; 
    DIR *dir  = opendir(path.c_str()); 
    vector<string> file_names; 
    while (entry  = readdir(dir)) { 
        string name = entry->d_name;
        if (strcmp(name.c_str(), ".") && strcmp(name.c_str(), "..")) { 
            file_names.push_back(name); 
        }
    } 

    sort(file_names.begin(), file_names.end()); 
    closedir(dir);
    return file_names; 
} 

void Forwarder::format_send_completed_msg(string image_id) { 
    cout << "[f] fscm" << endl;
    Emitter msg; 
    msg << BeginMap; 
    msg << Key << "MSG_TYPE" << Value << "FORWARD_END_READOUT"; 
    msg << Key << "IMAGE_ID" << Value << image_id; 
    msg << EndMap; 
    fmt_pub->publish_message(this->forward_consume_queue, msg.c_str()); 
} 
///////////////////////////////////////////////////////////////////////////

void Forwarder::format_look_for_work() { 
    cout << "[f] flfw" << endl;
    vector<string>::iterator it;
    map<string, string>::iterator mit;  
    map<string, string>::iterator tid; 
    cout << "readout SIZE: " << readout_img_ids.size() << endl;
    if (this->readout_img_ids.size() != 0 && this->header_info_dict.size() != 0) { 
        cout << "[x] img data exists" << endl; 
        for (it = this->readout_img_ids.begin(); it != this->readout_img_ids.end(); ) { 
            string img_id = *it; 
            mit = this->header_info_dict.find(img_id); 
            if (mit != this->header_info_dict.end()) { 
                this->readout_img_ids.erase(it); 
                string header_filename = this->header_info_dict[img_id]; 
                this->header_info_dict.erase(mit); 

                // do the work 
                Node n; 
                n["IMAGE_ID"] = img_id; 
                n["HEADER"] = header_filename; 
                format_assemble_img(n); 
            } 
            else it++; 
        } 
    } 
    else if (this->readout_img_ids.size() == 0 || this->header_info_dict.size() == 0) { 
        cout << "[x] no img data" << endl; 
        return; 
    } 
} 

///////////////////////////////////////////////////////////////////////////////
// Forward part 
///////////////////////////////////////////////////////////////////////////////

void Forwarder::forward_process_end_readout(Node n) { 
    string img_id = n["IMAGE_ID"].as<string>(); 
    string img_path = this->Work_Dir + "/FITS/" + img_id + ".fits"; 
    string dest_path = this->Target_Location + "/" + img_id + ".fits"; 
  
    // use bbcp to send file 
    ostringstream bbcp_cmd; 
    bbcp_cmd << "bbcp "
           << img_path
           << " " 
           << dest_path; 
    cout << bbcp_cmd.str() << endl; 
    system(bbcp_cmd.str().c_str()); 
    this->finished_image_work_list.push_back(img_id);
    cout << "[X] READOUT COMPLETE." << endl;
} 

void Forwarder::forward_process_take_images_done(Node n) { 
    cout << "get here" << endl;
    ostringstream message;
    string ack_id = n["ACK_ID"].as<string>();
    string reply_queue = n["REPLY_QUEUE"].as<string>();
    string msg_type = "AR_FWDR_TAKE_IMAGES_DONE_ACK ";
    string ack_bool = "True";
  
    Emitter msg; 
    msg << BeginMap; 
    msg << Key << "MSG_TYPE" << Value << msg_type; 
    msg << Key << "COMPONENT" << Value << this->Component; 
    msg << Key << "ACK_ID" << Value << ack_id; 
    msg << Key << "ACK_BOOL" << Value << ack_bool; 
    msg << Key << "RESULT_SET" << Value << Flow; 
        msg << BeginMap; 
        msg << Key << "FILENAME_LIST" << Value << Flow << finished_image_work_list; 
        msg << Key << "CHECKSUM_LIST" << Value << Flow << checksum_list;  
        msg << EndMap; 
    msg << EndMap; 
    cout << "[x] tid msg: " << endl; 
    cout << msg.c_str() << endl;
  
    this->fwd_pub->publish_message(reply_queue, msg.c_str());
    cout << "msg is replied to ..." << reply_queue << endl;
} 

int main() {
    Forwarder *fwdr = new Forwarder();
    fwdr->run();
    while(1) {
    }
}

void Forwarder::fetch_readout_image(string image_id, string dir_prefix) {
  // Iterate through raft_list
  // Foreman divide_work() method might have sent more than one raft,
  // so here we act upon one raft at a time.
  // The ccd_list is a vector that holds the ccds desired from this raft.
  // It might have the string 'ALL'...if so, fetch all ccds for this raft.

  for (int i = 0; i < this->visit_raft_list.size(); i++) {
    vector<string> ccd_list = this->visit_ccd_list_by_raft[i];
    fetch_readout_raft(this->visit_raft_list[i], ccd_list, image_id, dir_prefix);
  }

}

void Forwarder::fetch_readout_raft(string raft, vector<string> ccd_list, string image_id, string dir_prefix) {
  // put a map together with raft electronic board (source) for key, and ccd_list as value
  map<string, vector<string>> source_boards;
  if (ccd_list[0] == "ALL") {
    source_boards = All_Boards;
  }
  else {
    for (int i = 0; i < ccd_list.size(); i++) {
      int brd = Board_Layout[ccd_list[i]];
      string board = std::to_string(brd);

      if (source_boards.count(board)) {
        //board exists as a key already...
        source_boards[board].push_back(ccd_list[i]);
      }
      else {
        // Create new map key entry for this board
        source_boards.insert(pair<string,vector<string>>(board,vector<string>()));
        source_boards[board].push_back(ccd_list[i]);
      }
    }
  }
  // map of ccds by source boards is complete. Note: There are 3 source boards in a typical raft,
  // but the source_boards map generated above, may not include keys for all 3 source boards.
  // If ccd list is especially sparse, only one board might be included in map.
  this->fetch_reassemble_raft_image(raft, source_boards, image_id, dir_prefix);

}

void Forwarder::fetch_reassemble_raft_image(string raft, map<string, vector<string>> source_boards, string image_id, string dir_prefix) {
  // Fetch LocationSet for raft.
  // Examine each source in set...
  ostringstream raft_name;
  raft_name << "raft" << raft;
  string rafty = raft_name.str();
  IMS::Store store(rafty.c_str()); //DAQ Partitions must be set up to reflect DM name for a raft,
                                     // such as raft01, raft13, etc.

  IMS::Image image(image_id.c_str(), store);

  image.synopsis();

  DAQ::LocationSet sources = image.sources();

  DAQ::Location location;

  int board = 0; // Only way we know how to access a board is by its integer id.

  //The loop below processes each raft board (an individual source) one at a time.
  //In order to avoid boards that do not have desired CCDs on them, we check within
  //this loop; if board is not needed, we skip processing it. This is done by
  //converting the board counter to a string, and checking within the source_boards map
  //for a key representing the current board. If it exists, send board(location) to
  //reassemble process
  // FOR GREGG T: Is there a way to get a board number directly from API
  //rather than using the indirect counter method used here?
  while(sources.remove(location))
  {
      string board_str = std::to_string(board);
      if(source_boards.count(board_str)) {  // If current board source is in the source_boards mape
                                           // that we put together in the preceeding method...
        std::vector<string> ccds_for_board = source_boards[board_str];
        this->fetch_reassemble_process(raft, image_id, location, image, ccds_for_board, dir_prefix);
        board++;
      }
      else {
        continue;
      }
  }

  return;
}

// Above, the source boards are iterated through one at a time.
// If the requested raft/ccd(s) can be found within the current board, the needed CCD list
// for the current board is sent to this method along with the board location.
// These two args are used to extract the correct data.
// The other two args (raft and image_id) are used in constructing the output filename
//
// First, determine the number of CCDs in the ccds_for_board vector arg.
// the number of ccds + the name of each CCD in the vector will tell us how to decode the slice.
void Forwarder::fetch_reassemble_process(std::string raft, string image_id, const DAQ::Location& location, const IMS::Image& image, std::vector<string> ccds_for_board, string dir_prefix)
{
  IMS::Source source(location, image);

  IMS::Science slice(source);

  if(!slice) return;

  // Set up filehandles for this board. There must be a separate filehandle set for each CCD
  // to be fetched. CCDs to be fetched are listed in the ccds_for_board vector. Each CCD
  //will then have a set of 16 filehandles...one filehandle for each amp segment.

  uint64_t pixel = 0;
  uint64_t total_stripes = 0;
  uint64_t pixel_errors = 0;

  bool do_ccd0 = false;
  bool do_ccd1 = false;
  bool do_ccd2 = false;

  std::vector<std::ofstream> FH0;
  std::vector<std::ofstream> FH1;
  std::vector<std::ofstream> FH2;

  vector<string>::iterator it=ccds_for_board.begin();
  while(it!=ccds_for_board.end()){
        if(it[0] == "0") {
            do_ccd0 = true;
            this->fetch_set_up_filehandles(FH0, image_id, raft, it[0], dir_prefix);
        }
        if(it[0] == "1") {
            do_ccd1 = true;
            this->fetch_set_up_filehandles(FH1, image_id, raft, it[0], dir_prefix);
        }
        if(it[0] == "2") {
            do_ccd2 = true;
            this->fetch_set_up_filehandles(FH2, image_id, raft, it[0], dir_prefix);
        }
        ++it;
    }

  do
  {
    total_stripes += slice.stripes();
    IMS::Stripe* ccd0 = new IMS::Stripe [slice.stripes()];
    IMS::Stripe* ccd1 = new IMS::Stripe [slice.stripes()];
    IMS::Stripe* ccd2 = new IMS::Stripe [slice.stripes()];

    slice.decode012(ccd0, ccd1, ccd2);

    for(int s=0; s<slice.stripes(); ++s)
    {
      for(int amp=0; amp<N_AMPS; ++amp)
      {
        if (do_ccd0) {
          FH0[amp].write(reinterpret_cast<const char *>(&ccd0[s].segment[amp]), 1);
        }
      }

      for(int amp=0; amp<N_AMPS; ++amp)
      {
        if (do_ccd1) {
          FH1[amp].write(reinterpret_cast<const char *>(&ccd1[s].segment[amp]), 1);
        }
      }

      for(int amp=0; amp<N_AMPS; ++amp)
      {
        if (do_ccd2) {
          FH2[amp].write(reinterpret_cast<const char *>(&ccd2[s].segment[amp]), 1);
        }
      }


    delete [] ccd0;
    delete [] ccd1;
    delete [] ccd2;


    }
  }
  while(slice.advance());

  if (do_ccd0) 
    this->fetch_close_filehandles(FH0);
  if (do_ccd1) 
    this->fetch_close_filehandles(FH1);
  if (do_ccd2) 
    this->fetch_close_filehandles(FH2);

  return;

}
/*
void Forwarder::fetch_set_up_filehandles( std::vector<std::ofstream> &fh_set, string image_id, string raft, string ccd, string dir_prefix){
  for (int i=0; i < 16; i++) {
        std::ofstream fh;
        std::string seg;
        if (i < 10) {
            seg = "0" + to_string(i);
        }
        else {
            seg = to_string(i);
        }
        std::ostringstream fns;
        fns << dir_prefix << "/" \
                          << image_id \
                          << "--" << raft \
                          << "-ccd." << ccd \
                          << "_segment." << seg;

        fh.open(fns.str().c_str(), \
                std::ios::out | std::ios::app | std::ios::binary );
        fh_set.push_back(std::move(fh));  // The new, cool kid way to deal with smart pointers!
  }
}
*/


void Forwarder::fetch_set_up_filehandles( std::vector<std::ofstream> &fh_set, string image_id, string raft, string ccd, string dir_prefix){
  for (int i=0; i < 16; i++) {
        std::ofstream fh;
        std::string seg;
        if (i < 10) {
            seg = "0" + to_string(i);
        }
        else {
            seg = to_string(i);
        }
        std::ostringstream fns;
        fns << dir_prefix << "/" \
                          << image_id \
                          << "--" << raft \
                          << "-ccd." << ccd \
                          << "_segment." << seg;

        fh_set[i].open(fns.str().c_str(), \
                std::ios::out | std::ios::app | std::ios::binary );

        //fh_set.push_back(std::move(fh));  // The new, cool kid way to deal with smart pointers!
  }
}

void Forwarder::fetch_close_filehandles(std::vector<std::ofstream> &fh_set) {

  for (int i = 0; i < 16; i++) {
    fh_set[i].close();
  }

}


