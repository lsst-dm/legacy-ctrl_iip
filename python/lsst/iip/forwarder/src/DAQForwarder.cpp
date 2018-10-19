////////////////////////////////////////////////////////////////
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
#include <chrono>
#include <yaml-cpp/yaml.h>
#include "Consumer_impl.h"
#include "SimplePublisher.h"
#include "fitsio.h"
#include <errno.h>
#include "Exceptions.h"
#include "SimpleLogger.h"

#include "daq/Location.hh"
#include "daq/LocationSet.hh"

#include "ims/Store.hh"
#include "ims/Image.hh"
#include "ims/Source.hh"
#include "ims/Slice.hh"
#include "ims/Science.hh"
#include "ims/WaveFront.hh"

#include "rms/InstructionList.hh"
#include "rms/Instruction.hh"
#include <openssl/md5.h>
#include <boost/crc.hpp>

#define SECONDARY_HDU 2
#define STRING(s) STRING_EXPAND(s)
#define STRING_EXPAND(s) #s 
#define NAXIS1 576
#define NAXIS2 2048
#define N_AMPS 16
#define WFS_PIX_MASK 0x20000
#define SCIENCE_PIX_MASK 0x1FFFF
#define PIX_MASK 0x3FFFF
#define STRAIGHT_PIX_MASK 0x20000
#define DEBUG 1
#define METRIX 1
#define PRIVATE_BUFFER_SIZE  1024  // Used by crc32 code
#define L1_CFG_FILE_LOCATION  "../../L1SystemCfg.yaml"

using namespace std;
using namespace YAML;

BOOST_LOG_INLINE_GLOBAL_LOGGER_DEFAULT(my_logger, src::severity_logger_mt< severity_level >);

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
    std::map<string, map<string,string> > image_ids_to_jobs_map;

    std::string Session_ID = "";
    std::string Visit_ID = "";
    std::string Job_Num = "";
    std::string Target_Location = "/tmp/target";
    std::string Daq_Addr = "";
    std::string Work_Dir = ""; 
    std::string Src_Dir = ""; 
    std::string Name = ""; //such as FORWARDER_1
    std::string Lower_Name; //such as f1
    std::string Component = ""; //such as FORWARDER_1
    std::string Foreman_Reply_Queue = "";
    std::string Device_Type = "";
    std::string WFS_RAFT = "";
    std::string Checksum_Type = "";
    bool Checksum_Enabled = false;
    bool is_naxis_set = true;  // If true, registers will NOT be read
    long Naxis_1 = NAXIS1;
    long Naxis_2 = NAXIS2;
    int Num_Images = 0; 
    int ERROR_CODE_PREFIX; 
    std::string Telemetry_Queue = "telemetry_queue";
    std::vector<string> Segment_Names = {"00","01","02","03","04","05","06","07",\
                                         "10","11","12","13","14","15","16","17"};

    std::vector<string> Newest_Segment_Names = {"07","06","05","04","03","02","01","00",\
                                         "10","11","12","13","14","15","16","17"};

    // Works for Main Camera
    std::vector<string> New_Segment_Names = {"17","16","15","14","13","12","11","10",\
                                             "00","01","02","03","04","05","06","07"};

    // Works for ATS cam
    std::vector<string> ATS_Segment_Names = {"00","01","02","03","04","05","06","07",\
                                             "17","16","15","14","13","12","11","10"};

    
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
    
    string USER, PASSWD, BASE_BROKER_ADDR, FQN, HOSTNAME; 
    string IP_ADDR, CONSUME_QUEUE, USER_FORWARD_PUB, PASSWD_FORWARD_PUB;
    string USER_PUB, PASSWD_PUB, USER_FETCH_PUB, PASSWD_FETCH_PUB; 
    string USER_FORMAT_PUB, PASSWD_FORMAT_PUB;
    string FETCH_USER, FETCH_USER_PASSWD, FORMAT_USER, FORMAT_USER_PASSWD;  
    string FORWARD_USER, FORWARD_USER_PASSWD;
    string FETCH_USER_PUB, FETCH_USER_PUB_PASSWD, FORMAT_USER_PUB, FORMAT_USER_PUB_PASSWD; 
    string FORWARD_USER_PUB, FORWARD_USER_PUB_PASSWD;

    //vector<string> readout_img_ids; 
    std::map<string, map<string,string>> readout_img_ids; 
    //map<(pair<string, pair<string,string> >),string> img_to_raft_ccd_pair; 
    map<pair<string,pair<string,string> >, string> img_to_raft_ccd_pair; 
    map<string, vector<string> > img_to_raft_list; 
    map<string, vector<vector<string> > > img_to_raft_ccd_list; 
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
    void process_at_xfer_params(Node n);
    void process_take_images(Node n);
    void process_take_images_done(Node n);
    void process_end_readout(Node n);
    void process_at_end_readout(Node n);
    void process_header_ready(Node n); 

    void process_fetch(Node n);
    void process_at_fetch(Node n);
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

    int fetch_readout_image(string image_id, string dir_prefix);
    int fetch_readout_raft(string raft, vector<string> ccd_list, string image_id, string dir_prefix);
    int fetch_reassemble_raft_image(string raft, map<string, vector<string>> source_boards, string image_id, string dir_prefix);
    int fetch_reassemble_process(string raft, string image_id, const DAQ::Location& location, const IMS::Image& image, std::vector<string> ccds_for_board, string dir_prefix);
    int fetch_at_reassemble_process(string raft, string ccd, string image_id, string dir_prefix);
    void get_register_metadata(const DAQ::Location& location, const IMS::Image& image);
    void fetch_set_up_filehandles(std::vector<std::ofstream*> &fh_set, string image_id, string raft, string ccd, string dir_prefix);
    void fetch_set_up_at_filehandles(std::vector<std::ofstream*> &fh_set, string image_id, string dir_prefix);
    void fetch_close_filehandles(std::vector<std::ofstream*> &fh_set);
    int check_for_image_existence(std::string);
    void send_telemetry(int, std::string);

    long* format_read_img_segment(const char*);
    void format_write_img(std::string, std::string, std::string);
    void format_assemble_img(Node);
    void format_send_completed_msg(std::string);
    void format_look_for_work(std::string); 
    void format_process_end_readout(Node); 
    void format_get_header(Node); 
    vector<string> format_list_files(string); 
    string format_get_binary_path(std::string); 

    void forward_process_end_readout(Node); 
    void forward_process_take_images_done(Node); 
    std::string forward_send_result_set(std::string, std::string, std::string);
    std::string forward_calculate_md5_checksum(std::string);
    std::string forward_calculate_crc32_checksum(std::string);
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
    { "AT_NEW_VISIT", &Forwarder::process_new_visit},
    { "AR_FWDR_HEALTH_CHECK", &Forwarder::process_health_check},
    { "PP_FWDR_HEALTH_CHECK", &Forwarder::process_health_check},
    { "AT_FWDR_HEALTH_CHECK", &Forwarder::process_health_check},
    { "AR_FWDR_XFER_PARAMS", &Forwarder::process_xfer_params},
    { "PP_FWDR_XFER_PARAMS", &Forwarder::process_xfer_params},
    { "AT_FWDR_XFER_PARAMS", &Forwarder::process_at_xfer_params},
    { "AR_FWDR_TAKE_IMAGES", &Forwarder::process_take_images},
    { "PP_TAKE_IMAGES", &Forwarder::process_take_images},
    { "AT_TAKE_IMAGES", &Forwarder::process_take_images},
    { "AR_FWDR_END_READOUT", &Forwarder::process_end_readout},
    { "PP_FWDR_END_READOUT", &Forwarder::process_end_readout},
    { "AT_FWDR_END_READOUT", &Forwarder::process_at_end_readout},
    { "AR_TAKE_IMAGES_DONE", &Forwarder::process_take_images_done},
    { "PP_TAKE_IMAGES_DONE", &Forwarder::process_take_images_done},
    { "AT_TAKE_IMAGES_DONE", &Forwarder::process_take_images_done}, 
    { "AR_FWDR_HEADER_READY", &Forwarder::process_header_ready }, 
    { "PP_FWDR_HEADER_READY", &Forwarder::process_header_ready }, 
    { "AT_FWDR_HEADER_READY", &Forwarder::process_header_ready } 
};

//The next three handlers are essentially acks...
map<string, funcptr> on_fetch_message_actions = {
    { "FETCH_HEALTH_CHECK_ACK", &Forwarder::process_fetch_health_check_ack},
    { "AR_FETCH_ACK", &Forwarder::process_fetch_ack},
    { "PP_FETCH_ACK", &Forwarder::process_fetch_ack},
    { "AT_FETCH_ACK", &Forwarder::process_fetch_ack}

};

map<string, funcptr> on_format_message_actions = {
    { "FORMAT_HEALTH_CHECK_ACK", &Forwarder::process_format_health_check_ack},
    { "AR_FORMAT_ACK", &Forwarder::process_format_ack},
    { "PP_FORMAT_ACK", &Forwarder::process_format_ack},
    { "AT_FORMAT_ACK", &Forwarder::process_format_ack}

};

map<string, funcptr> on_forward_message_actions = {
    { "FORWARD_HEALTH_CHECK_ACK", &Forwarder::process_forward_health_check_ack},
    { "AR_FORWARD_ACK", &Forwarder::process_forward_ack},
    { "PP_FORWARD_ACK", &Forwarder::process_forward_ack},
    { "AT_FORWARD_ACK", &Forwarder::process_forward_ack}

};


//Forwarder Component message actions
//This handler is for messages from Primary Forwarder to fetch thread
map<string, funcptr> on_forwarder_to_fetch_message_actions = {
    { "FETCH_HEALTH_CHECK", &Forwarder::process_fetch_health_check},
    { "FETCH_END_READOUT", &Forwarder::process_fetch},
    { "FETCH_AT_END_READOUT", &Forwarder::process_at_fetch},
    { "FETCH_TAKE_IMAGES_DONE", &Forwarder::process_fetch},
    { "AR_FETCH", &Forwarder::process_fetch},
    { "PP_FETCH", &Forwarder::process_fetch},
    { "AT_FETCH", &Forwarder::process_fetch}
};

//This handler is for messages from Primary Forwarder to format thread
map<string, funcptr> on_forwarder_to_format_message_actions = {
    { "FORMAT_HEALTH_CHECK", &Forwarder::process_format_health_check},
    { "AR_FORMAT", &Forwarder::process_format},
    { "PP_FORMAT", &Forwarder::process_format},
    { "SP_FORMAT", &Forwarder::process_format}, 
    { "FORMAT_END_READOUT", &Forwarder::format_process_end_readout}, 
    { "FORMAT_HEADER_READY", &Forwarder::format_get_header}, 
    { "FORMAT_TAKE_IMAGES_DONE", &Forwarder::process_format}
};

//This handler is for messages from Primary Forwarder to forward thread
map<string, funcptr> on_forwarder_to_forward_message_actions = {
    { "FORWARD_HEALTH_CHECK", &Forwarder::process_forward_health_check},
    { "AR_FORWARD", &Forwarder::process_forward},
    { "TAKE_IMAGES_DONE", &Forwarder::process_forward},
    { "PP_FORWARD", &Forwarder::process_forward},
    { "SP_FORWARD", &Forwarder::process_forward}, 
    { "FORWARD_END_READOUT", &Forwarder::forward_process_end_readout}, 
    { "FORWARD_TAKE_IMAGES_DONE", &Forwarder::forward_process_take_images_done}  
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
    // init_log 
    init_log("Forwarder");

    // Read config file
    Node config_file;
    try {
        config_file = LoadFile("./ForwarderCfg.yaml");
        LOGGER(my_logger::get(), debug) << "Reading ForwarderCfg config file."; 
    }
    catch (YAML::BadFile& e) {
        // FIX better catch clause...at LEAST a log message
        LOGGER(my_logger::get(), critical) << "Error reading ForwarderCfg.yaml file.";
        // FIX Go to Fault State instead?
        exit(EXIT_FAILURE);
    }

    Node root;
    string NAME, BASE_BROKER_ADDR, FQN, HOSTNAME, IP_ADDR;
    ERROR_CODE_PREFIX = 5600; 
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
        this->BASE_BROKER_ADDR = root["BASE_BROKER_ADDR"].as<string>(); 

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

        //this->WFS_RAFT = root["ATS"]["WFS_RAFT"].as<string>();
        //cout << "Setting WFS_RAFT class var to:  " << this->WFS_RAFT << endl << endl << endl;
    }
    catch (YAML::TypedBadConversion<string>& e) {
        LOGGER(my_logger::get(), critical) << e.what();
        LOGGER(my_logger::get(), critical) << "In ForwarderCfg.yaml, cannot read required elements from this file.";
        // FIX Set Fault State instead?
        exit(EXIT_FAILURE);
    }

    // Read L1 config file
    Node L1_config_file;
    try {
        L1_config_file = LoadFile(L1_CFG_FILE_LOCATION);
    }
    catch (YAML::BadFile& e) {
        LOGGER(my_logger::get(), critical) << "Error reading L1SystemCfg.yaml file.";
        cout << "Error reading L1SystemCfg.yaml file." << endl;
        // FIX Set Fault State instead?
        exit(EXIT_FAILURE);
    }

    try {
        Node cdm;
        cdm = L1_config_file["ROOT"];
        if((cdm["ARCHIVE"]["CHECKSUM_ENABLED"].as<string>()) == "yes") {
            this->Checksum_Enabled = true;
            this->Checksum_Type = cdm["ARCHIVE"]["CHECKSUM_TYPE"].as<string>();
        }
        else {
            this->Checksum_Enabled = false;
        }
    }
    catch (YAML::TypedBadConversion<string>& e) {
        cout << e.what() << endl;
        cout << "ERROR: In L1SystemCfg.yaml, can't read required elements from this file." << endl;
    }


    setup_consumers(BASE_BROKER_ADDR);
    setup_publishers(BASE_BROKER_ADDR);
    LOGGER(my_logger::get(), debug) << "Forwarder construction complete.";  
    
}

void Forwarder::setup_consumers(string BASE_BROKER_ADDR){
    LOGGER(my_logger::get(), debug) << "Entering setup_consumers function."; 
    //Consumers for Primary Forwarder
    ostringstream full_broker_url;
    full_broker_url << "amqp://" << this->USER << ":" << this->PASSWD << this->BASE_BROKER_ADDR ;
    LOGGER(my_logger::get(), debug) << "Consumer broker URL is: " << full_broker_url.str();
    from_foreman_consumer = new Consumer(full_broker_url.str(), this->consume_queue);

    ostringstream consume_queue1;
    consume_queue1 << this->consume_queue << "_from_fetch";
    from_fetch_consumer = new Consumer(full_broker_url.str(), consume_queue1.str());
    LOGGER(my_logger::get(), debug) << "Consuming from queue: " << consume_queue1.str();

    ostringstream consume_queue2;
    consume_queue2 << this->consume_queue << "_from_format";
    from_format_consumer = new Consumer(full_broker_url.str(), consume_queue2.str());
    LOGGER(my_logger::get(), debug) << "Consuming from queue: " << consume_queue2.str();

    ostringstream consume_queue3;
    consume_queue3 << this->consume_queue << "_from_forward";
    ostringstream from_fwd_broker_url;
    from_fwd_broker_url << "amqp://" << this->USER << ":" << this->PASSWD << this->BASE_BROKER_ADDR ;
    from_forward_consumer = new Consumer(full_broker_url.str(), consume_queue3.str());
    LOGGER(my_logger::get(), debug) << "Consumer broker URL is: " << from_fwd_broker_url.str();
    LOGGER(my_logger::get(), debug) << "Consuming from queue: " << consume_queue3.str();

    //Consumers for sub-components
    //ostringstream consume_queue;

    ostringstream full_broker_url2;
    full_broker_url2 << "amqp://" << this->FETCH_USER << ":" << this->FETCH_USER_PASSWD << this->BASE_BROKER_ADDR ;
    from_forwarder_to_fetch = new Consumer(full_broker_url.str(), this->fetch_consume_queue);
    LOGGER(my_logger::get(), debug) << "Consumer broker URL is: " << full_broker_url2.str();
    LOGGER(my_logger::get(), debug) << "Consuming from queue: " << this->fetch_consume_queue;

    ostringstream full_broker_url3;
    full_broker_url3 << "amqp://" << this->FORMAT_USER << ":" << this->FORMAT_USER_PASSWD << this->BASE_BROKER_ADDR;
    from_forwarder_to_format = new Consumer(full_broker_url.str(), this->format_consume_queue);
    LOGGER(my_logger::get(), debug) << "Consumer broker URL is: " << full_broker_url3.str();
    LOGGER(my_logger::get(), debug) << "Consuming from queue: " << this->format_consume_queue;
    //cout << this->format_consume_queue << endl; 

    ostringstream full_broker_url4;
    full_broker_url4 << "amqp://" << this->FORWARD_USER << ":" << this->FORWARD_USER_PASSWD << this->BASE_BROKER_ADDR ;
    from_forwarder_to_forward = new Consumer(full_broker_url.str(), this->forward_consume_queue);
    LOGGER(my_logger::get(), debug) << "Consumer broker URL is: " << full_broker_url4.str();
    LOGGER(my_logger::get(), debug) << "Consuming from queue: " << this->forward_consume_queue;

    LOGGER(my_logger::get(), debug) << "Finished setting broker urls for consumers"; 
}

void Forwarder::run() {
    LOGGER(my_logger::get(), debug) << "Entering run function."; 
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

    LOGGER(my_logger::get(), debug) << "Finished setting up threads for consumers."; 
}

void *Forwarder::run_thread(void *pargs) {
    LOGGER(my_logger::get(), debug) << "Entering run_thread function."; 

    arg_struct *params = ((arg_struct *) pargs);
    Consumer *consumer = params->consumer;
    Forwarder *forwarder = params->forwarder;
    callback<Forwarder> on_msg = params->funcptr;

    consumer->run<Forwarder>(forwarder, on_msg);
    LOGGER(my_logger::get(), debug) << "Finished setting up thread."; 
}


void Forwarder::setup_publishers(string BASE_BROKER_ADDR){
    LOGGER(my_logger::get(), debug) << "Entering setup_publishers function."; 
    //Publishers
    ostringstream full_broker_url;
    full_broker_url << "amqp://" << this->USER_PUB << ":" << this->PASSWD_PUB << this->BASE_BROKER_ADDR;
    LOGGER(my_logger::get(), debug) << "Publisher broker URL is: " << full_broker_url.str();
    FWDR_pub = new SimplePublisher(full_broker_url.str());

    ostringstream full_broker_url1;
    full_broker_url1 << "amqp://" << this->USER_FETCH_PUB << ":" << this->PASSWD_FETCH_PUB << this->BASE_BROKER_ADDR;
    LOGGER(my_logger::get(), debug) << "Publisher broker URL is: " << full_broker_url1.str();
    FWDR_to_fetch_pub = new SimplePublisher(full_broker_url1.str());

    ostringstream full_broker_url2;
    full_broker_url2 << "amqp://" << this->USER_FORMAT_PUB << ":" << this->PASSWD_FORMAT_PUB << this->BASE_BROKER_ADDR;
    LOGGER(my_logger::get(), debug) << "Publisher broker URL is: " << full_broker_url2.str();
    FWDR_to_format_pub = new SimplePublisher(full_broker_url2.str());

    ostringstream full_broker_url3;
    full_broker_url3 << "amqp://" << this->USER_FORWARD_PUB << ":" << this->PASSWD_FORWARD_PUB << this->BASE_BROKER_ADDR;
    LOGGER(my_logger::get(), debug) << "Publisher broker URL is: " << full_broker_url3.str();
    FWDR_to_forward_pub = new SimplePublisher(full_broker_url3.str());

    ostringstream full_broker_url4;
    full_broker_url4 << "amqp://" << this->FETCH_USER_PUB << ":" << this->FETCH_USER_PUB_PASSWD << this->BASE_BROKER_ADDR;
    LOGGER(my_logger::get(), debug) << "Publisher broker URL is: " << full_broker_url4.str();
    fetch_pub = new SimplePublisher(full_broker_url4.str());

    ostringstream full_broker_url5;
    full_broker_url5 << "amqp://" << this->FORMAT_USER_PUB << ":" << this->FORMAT_USER_PUB_PASSWD << this->BASE_BROKER_ADDR;
    LOGGER(my_logger::get(), debug) << "Publisher broker URL is: " << full_broker_url5.str();
    fmt_pub = new SimplePublisher(full_broker_url5.str());

    ostringstream full_broker_url6;
    full_broker_url6 << "amqp://" << this->FORWARD_USER_PUB << ":" << this->FORWARD_USER_PUB_PASSWD << this->BASE_BROKER_ADDR;
    LOGGER(my_logger::get(), debug) << "Publisher broker URL is: " << full_broker_url6.str();
    fwd_pub = new SimplePublisher(full_broker_url6.str());
    
    LOGGER(my_logger::get(), debug) << "Setting up publishers is complete."; 
}



//Messages received by Primary Forwarder from Foreman
void Forwarder::on_foreman_message(string body) {
    LOGGER(my_logger::get(), debug) << "In forwarder callback that receives msgs from AR foreman";
    LOGGER(my_logger::get(), debug) << "-----------Message Body Is:------------";
    LOGGER(my_logger::get(), debug) << body;
    LOGGER(my_logger::get(), debug) << "----------------------";
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_foreman_message_actions[message_type];
    (this->*action)(node);
}

//Messages received by Primary Forwarder from fetch thread
void Forwarder::on_fetch_message(string body) {
    LOGGER(my_logger::get(), debug) << "In main forwarder callback that receives msgs from fetch thread";
    LOGGER(my_logger::get(), debug) << "-----------Message Body Is:------------";
    LOGGER(my_logger::get(), debug) << body;
    LOGGER(my_logger::get(), debug) << "----------------------";
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_fetch_message_actions[message_type];
    (this->*action)(node);
}

//Messages received by Primary Forwarder from format thread
void Forwarder::on_format_message(string body) {
    LOGGER(my_logger::get(), debug) << "In main forwarder callback that receives msgs from format thread";
    LOGGER(my_logger::get(), debug) << "-----------Message Body Is:------------";
    LOGGER(my_logger::get(), debug) << body;
    LOGGER(my_logger::get(), debug) << "----------------------";
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_format_message_actions[message_type];
    (this->*action)(node);
}

//Messages received by Primary Forwarder from forwardthread
void Forwarder::on_forward_message(string body) {
    LOGGER(my_logger::get(), debug) << "In main forwarder callback that receives msgs from forward thread";
    LOGGER(my_logger::get(), debug) << "-----------Message Body Is:------------";
    LOGGER(my_logger::get(), debug) << body;
    LOGGER(my_logger::get(), debug) << "----------------------";
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_forward_message_actions[message_type];
    (this->*action)(node);
}



//Messages received by the fetch, format, and forward threads
void Forwarder::on_forwarder_to_fetch_message(string body) {
    LOGGER(my_logger::get(), debug) << "In fetch callback that receives msgs from main forwarder thread";
    LOGGER(my_logger::get(), debug) << "-----------Message Body Is:------------";
    LOGGER(my_logger::get(), debug) << body;
    LOGGER(my_logger::get(), debug) << "----------------------";
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_forwarder_to_fetch_message_actions[message_type];
    (this->*action)(node);
}

void Forwarder::on_forwarder_to_format_message(string body) {
    LOGGER(my_logger::get(), debug) << "In format callback that receives msgs from main forwarder thread";
    LOGGER(my_logger::get(), debug) << "-----------Message Body Is:------------";
    LOGGER(my_logger::get(), debug) << body;
    LOGGER(my_logger::get(), debug) << "----------------------";
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_forwarder_to_format_message_actions[message_type];
    (this->*action)(node);
}

void Forwarder::on_forwarder_to_forward_message(string body) {
    LOGGER(my_logger::get(), debug) << "In forward callback that receives msgs from main forwarder thread";
    LOGGER(my_logger::get(), debug) << "-----------Message Body Is:------------";
    LOGGER(my_logger::get(), debug) << body;
    LOGGER(my_logger::get(), debug) << "----------------------";
    Node node = Load(body);
    string message_type = node["MSG_TYPE"].as<string>();
    funcptr action = on_forwarder_to_forward_message_actions[message_type];
    (this->*action)(node);
}


//Message action handler methods...
void Forwarder::process_new_visit(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_new_visit function."; 
    return;
}

void Forwarder::process_health_check(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_health_check function."; 
    string ack_id = n["ACK_ID"].as<string>();
    string reply_queue = n["REPLY_QUEUE"].as<string>();
    string message_type = n["MSG_TYPE"].as<string>();
    string msg_type = message_type + "_ACK"; //Add _ACK to end of msg_type and not worry about dev type
    string ack_bool = "True";

    ostringstream message;
    message << "{ MSG_TYPE: " << msg_type
            << ", COMPONENT: " << this->Component
            << ", ACK_ID: " << ack_id
            << ", ACK_BOOL: " << ack_bool << "}";

    FWDR_pub->publish_message(reply_queue, message.str());
    LOGGER(my_logger::get(), debug) << "Health Check request Message, ACK sent to: " \
                                    << reply_queue << endl;
    LOGGER(my_logger::get(), debug) << "Message sent is: " << message.str() << endl;
    LOGGER(my_logger::get(), info) << "Processing health check message complete."; 
    return;
}

void Forwarder::process_xfer_params(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_xfer_params function."; 
    LOGGER(my_logger::get(), debug) << "Incoming message is: " << n;

    string Image_ID = n["IMAGE_ID"].as<string>();
    LOGGER(my_logger::get(), debug) << "Image_ID has been assigned: " << Image_ID;

    this->Device_Type = "AR";
    this->readout_img_ids[Image_ID]["DEVICE"] = "AR";

    Node p = n["XFER_PARAMS"];
    LOGGER(my_logger::get(), debug) << "Incoming xfer_params is: " << p;

    //this->visit_raft_list.clear();
    this->img_to_raft_list[Image_ID] = p["RAFT_LIST"].as<vector<string> >();
    LOGGER(my_logger::get(), debug) << "RAFT_LIST has been assigned to class map variable.";

    //this->visit_ccd_list_by_raft.clear();
    this->img_to_raft_ccd_list[Image_ID] = p["RAFT_CCD_LIST"].as<std::vector<std::vector<string> > >();
    LOGGER(my_logger::get(), debug) << "RAFT_CCD_LIST has been assigned to map class variable.";

    //this->Session_ID = n["SESSION_ID"].as<string>();
    this->readout_img_ids[Image_ID]["SESSION"] = n["SESSION_ID"].as<string>();
    //LOGGER(my_logger::get(), debug) << "SESSION_ID has been assigned: " << this->Session_ID;

    string Job_Num = n["JOB_NUM"].as<string>();
    this->readout_img_ids[Image_ID]["JOB_NUM"] = Job_Num;
    LOGGER(my_logger::get(), debug) << "JOB_NUM has been assigned: " << Job_Num;

    string Target_Location = n["TARGET_LOCATION"].as<string>();
    this->readout_img_ids[Image_ID]["TARGET_LOCATION"] = Target_Location;
    LOGGER(my_logger::get(), debug) << "TARGET_LOCATION has been assigned: " << Target_Location;

    string reply_queue = n["REPLY_QUEUE"].as<string>();
    this->readout_img_ids[Image_ID]["REPLY_QUEUE"] = reply_queue;
    LOGGER(my_logger::get(), debug) << reply_queue <<" has been assigned to: " << Image_ID;

    string ack_id = n["ACK_ID"].as<string>();
    this->readout_img_ids[Image_ID]["ACK_ID"] = ack_id;
    LOGGER(my_logger::get(), debug) << "ACK_ID has been assigned: " << ack_id;

    // Set READOUT initial state to "no"
    this->readout_img_ids[Image_ID]["READOUT"] = "no";

    //this->Visit_ID = n["VISIT_ID"].as<string>();
    //cout << "After setting VISIT_ID" << endl;


    string message_type = "AR_FWDR_XFER_PARAMS_ACK";
    string ack_bool = "false";

    ostringstream message;
    message << "{ MSG_TYPE: " << message_type
            << ", COMPONENT: " << this->Component
            << ", ACK_ID: " << ack_id
            << ", ACK_BOOL: " << ack_bool << "}";

    FWDR_pub->publish_message(reply_queue, message.str());
    LOGGER(my_logger::get(), debug) << "AR_XFER_PARAMS_ACK is sent to: " << reply_queue; 
    LOGGER(my_logger::get(), debug) << "Message is: " << message.str(); 
    LOGGER(my_logger::get(), info) << "Processing transfer params is complete."; 
    return;
}

void Forwarder::process_at_xfer_params(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_at_xfer_params function."; 
    LOGGER(my_logger::get(), debug) << "Incoming message is: " << n;

    string Image_ID = n["IMAGE_ID"].as<string>();
    LOGGER(my_logger::get(), debug) << "Image_ID has been assigned: " << Image_ID;

    this->Device_Type = "AT";
    this->readout_img_ids[Image_ID]["DEVICE"] = "AT";

    Node p = n["XFER_PARAMS"];
    LOGGER(my_logger::get(), debug) << "Incoming xfer_params is: " << p;

    this->img_to_raft_list[Image_ID] = p["RAFT_LIST"].as<vector<string>>();
    LOGGER(my_logger::get(), debug) << "RAFT_LIST has been assigned to class map variable.";

    this->img_to_raft_ccd_list[Image_ID] = p["RAFT_CCD_LIST"].as<vector<vector<string>>>();
    LOGGER(my_logger::get(), debug) << "RAFT_CCD_LIST has been assigned to map class variable.";

    this->readout_img_ids[Image_ID]["SESSION"] = n["SESSION_ID"].as<string>();

    string Job_Num = n["JOB_NUM"].as<string>();
    this->readout_img_ids[Image_ID]["JOB_NUM"] = Job_Num;
    LOGGER(my_logger::get(), debug) << "JOB_NUM has been assigned: " << Job_Num;

    string Target_Location = n["TARGET_LOCATION"].as<string>();
    this->readout_img_ids[Image_ID]["TARGET_LOCATION"] = Target_Location;
    LOGGER(my_logger::get(), debug) << "TARGET_LOCATION has been assigned: " << Target_Location;

    string reply_queue = n["REPLY_QUEUE"].as<string>();
    this->readout_img_ids[Image_ID]["REPLY_QUEUE"] = reply_queue;
    LOGGER(my_logger::get(), debug) << reply_queue <<" has been assigned to: " << Image_ID;

    string ack_id = n["ACK_ID"].as<string>();
    this->readout_img_ids[Image_ID]["ACK_ID"] = ack_id;
    LOGGER(my_logger::get(), debug) << "ACK_ID has been assigned: " << ack_id;

    //this->Visit_ID = n["VISIT_ID"].as<string>();
    //cout << "After setting VISIT_ID" << endl;

    this->readout_img_ids[Image_ID]["READOUT_FINISHED"] = "no";
    this->readout_img_ids[Image_ID]["HEADER_FINISHED"] = "no";

    // Set READOUT initial state to "no"
    this->readout_img_ids[Image_ID]["READOUT"] = "no";


    string message_type = "AT_FWDR_XFER_PARAMS_ACK";
    string ack_bool = "true";
    ostringstream message;
    message << "{ MSG_TYPE: " << message_type
            << ", COMPONENT: " << this->Component
            << ", ACK_ID: " << ack_id
            << ", ACK_BOOL: " << ack_bool << "}";

    FWDR_pub->publish_message(reply_queue, message.str());
    LOGGER(my_logger::get(), debug) << "AT_XFER_PARAMS_ACK is sent to: " << reply_queue; 
    LOGGER(my_logger::get(), debug) << "Message is: " << message.str(); 
    LOGGER(my_logger::get(), info) << "Processing at_transfer params is complete."; 

    return;
}

void Forwarder::process_take_images(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_take_images function."; 
    this->Num_Images = n["NUM_IMAGES"].as<int>();;
    cout << "Take Image Message...should be some tasty params here" << endl;
    return;
}

void Forwarder::process_end_readout(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_end_readout function."; 
    // Send IMAGE_ID to fetch thread...use message broker queue as work queue
    //If ForwarderCfg.yaml DAQ val == 'API', draw from actual DAQ emulator,
    //else, DAQ val will equal a path where files can be found.

    // Build map of job_nums and ack_ids by image_id for other threads to use
    // The data structure is a map within a map
    string image_id = n["IMAGE_ID"].as<string>();
    string job_num = n["JOB_NUM"].as<string>();
    string ack_id = n["ACK_ID"].as<string>();
    std::map<string,string> inner;
    inner.insert(std::make_pair("JOB_NUM",job_num));
    inner.insert(std::make_pair("ACK_ID",ack_id));
    this->image_ids_to_jobs_map.insert(std::make_pair(image_id, inner));

    image_id_list.push_back(image_id);
    string msg_type = "FETCH_END_READOUT";
    ostringstream message;
    message << "{MSG_TYPE: " << msg_type
            << ", IMAGE_ID: " << image_id << "}";
    this->FWDR_to_fetch_pub->publish_message(this->fetch_consume_queue, message.str());
    LOGGER(my_logger::get(), debug) << "FETCH_END_READOUT is sent to: " << this->fetch_consume_queue; 
    LOGGER(my_logger::get(), debug) << "Message is: " << message.str(); 
    return;
}

void Forwarder::process_at_end_readout(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_at_end_readout function."; 
    // Send IMAGE_ID to fetch thread...use message broker queue as work queue
    //If ForwarderCfg.yaml DAQ val == 'API', draw from actual DAQ emulator,
    //else, DAQ val will equal a path where files can be found.

    string image_id = n["IMAGE_ID"].as<string>();
    image_id_list.push_back(image_id);
    string msg_type = "FETCH_AT_END_READOUT";
    ostringstream message;
    message << "{MSG_TYPE: " << msg_type
            << ", IMAGE_ID: " << image_id << "}";
    this->FWDR_to_fetch_pub->publish_message(this->fetch_consume_queue, message.str());
    LOGGER(my_logger::get(), debug) << "FETCH_AT_END_READOUT is sent to: " \
                                    << this->fetch_consume_queue; 
    LOGGER(my_logger::get(), debug) << "Message is: " << message.str(); 
    return;
}

///////////////////////////////////////////////////////////////////
// FETCH THREAD
///////////////////////////////////////////////////////////////////

//////////////////////////////////////
//  FETCH METHODS FOR AT PROCESSING
//////////////////////////////////////
void Forwarder::process_at_fetch(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_at_fetch function."; 

    string image_id = n["IMAGE_ID"].as<string>();
    int retval = 0;
    string raft = this->img_to_raft_list[image_id][0];
    string ccd = this->img_to_raft_ccd_list[image_id][0][0]; 
    LOGGER(my_logger::get(), debug) << "Process_AT_Fetch, RAFT string is: " << raft << ", and CCD is: " << ccd;
    ostringstream cmd;
    ostringstream rmcmd;
    ostringstream filepath;
    ostringstream dir_prefix;

    dir_prefix << this->Work_Dir << "/" << image_id;
    filepath << dir_prefix.str() << "/" \
                                 << raft << "/" \
                                 << ccd;
    cmd << "mkdir -p " << filepath.str();
    const std::string tmpstr = cmd.str();
    const char* cmdstr = tmpstr.c_str();
    system(cmdstr);

    LOGGER(my_logger::get(), debug) << "Directory " << filepath << " is created.";
    LOGGER(my_logger::get(), debug) << "Created directories for image segments."; 

    retval = this->fetch_at_reassemble_process(raft, ccd, image_id, filepath.str());

    if(retval == 1) {
           ostringstream desc;
           desc << "Forwarder Fetch Error: Found no image in Catalog for " \
                << image_id << ". Bailing from Readout." << endl;
           this->send_telemetry(1, desc.str());
           this->readout_img_ids.erase(image_id); 
           return;
     }
     if(retval == 2) {
           ostringstream desc;
           desc << "Forwarder Fetch Error: No data slices available for " \
                << image_id << ". Bailing from Readout." << endl;
           this->send_telemetry(2, desc.str());
           this->readout_img_ids.erase(image_id); 
           return;
     }
    return;
}


int Forwarder::fetch_at_reassemble_process(std::string raft, string ccd, \
                                           string image_id, string filepath) {

    LOGGER(my_logger::get(), debug) << "Entering fetch_at_reassemble_process function."; 
    int retval = 0;

    IMS::Store store(raft.c_str()); //DAQ Partitions must be set up to reflect DM name for a raft,
                                    // such as raft01, raft13, etc.

    // This tmp code checks for the existence of the image name in the DAQ catalog.
    if ((this->check_for_image_existence(image_id)) == 0) {
        cout << "Found an image that exists in Catalog. Fetching " << image_id << " now." << endl;
        retval = 0;
    }
    else {
        cout << "ALERT - ALERT" << endl;
        cout << "Found no image in Catalog for " << image_id << ". Bailing from Readout." << endl;
        ostringstream desc;
        desc << "Found no image in Catalog for " << image_id << ". Bailing from Readout." << endl;
        return(1);
    }

    IMS::Image image(image_id.c_str(), store);

    DAQ::LocationSet sources = image.sources();

    uint64_t total_stripes = 0;

    DAQ::Location location;

    while(sources.remove(location)) {

        // Set image array NAXIS values for format thread...
        this->get_register_metadata(location, image);

        IMS::Source source(location, image);
  
        IMS::WaveFront slice(source);

        // Bail out if we have no slice to process
        if(!slice) return(2);

        // Filehandle set for ATS CCD will then have a set of 
        // 16 filehandles...one filehandle for each amp segment.
  
        std::vector<std::ofstream*> FH_ATS;
        this->fetch_set_up_at_filehandles(FH_ATS, image_id, filepath);
  
            do {
                total_stripes += slice.stripes();
                IMS::Stripe* ccd0 = new IMS::Stripe [slice.stripes()];
    
                slice.decode(ccd0);
    
                for(int s=0; s<slice.stripes(); ++s) {
                    for(int amp=0; amp<N_AMPS; ++amp) {
                        int32_t X = STRAIGHT_PIX_MASK ^ ((ccd0[s].segment[amp]));
                        FH_ATS[amp]->write(reinterpret_cast<const char *>(&X), 4); //32 bits...
                    }
                }
    
                delete [] ccd0;
            } while(slice.advance());
  
      this->fetch_close_filehandles(FH_ATS);
      //this->img_to_raft_ccd_pair[image_id][make_pair(raft,ccd)] = filepath;
      this->img_to_raft_ccd_pair[make_pair(image_id,make_pair(raft,ccd))] = filepath;
      string new_msg_type = "FORMAT_END_READOUT";
      ostringstream msg;
      msg << "{MSG_TYPE: " << new_msg_type
          << ", IMAGE_ID: " << image_id
          << ", RAFT: " << raft
          << ", CCD: " << ccd
          << ", PATH: " << filepath << "}";
      this->fetch_pub->publish_message(this->format_consume_queue, msg.str());
      LOGGER(my_logger::get(), debug) << "FORMAT_END_READOUT is sent to: " \
                                      << this->format_consume_queue; 
      LOGGER(my_logger::get(), debug) << "Message is: " << msg; 
  }
  return retval;
}


void Forwarder::fetch_set_up_at_filehandles( std::vector<std::ofstream*> &fh_set, 
                                             string image_id, 
                                             string full_dir_prefix){

    LOGGER(my_logger::get(), debug) << "Entering fetch_set_up_at_filehandles function."; 

    for (int i=0; i < 16; i++) {
        std::ostringstream fns;
        fns << full_dir_prefix << "/" \
                               << image_id \
                               << "--AUXTEL" \
                               << "-ccd.ATS_CCD" \
                               << "_segment." << this->ATS_Segment_Names[i];

        std::ofstream * fh = new std::ofstream(fns.str(), std::ios::out | std::ios::binary );
        fh_set.push_back(fh); 
    }
    LOGGER(my_logger::get(), debug) << "Finished setting up file handlers for image segments."; 
}


void Forwarder::process_take_images_done(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_take_images_done function."; 
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
    LOGGER(my_logger::get(), debug) << "FETCH_TAKE_IMAGES_DONE is sent to: " << this->fetch_consume_queue; 
    LOGGER(my_logger::get(), debug) << "Message is: " << msg; 
}

/////////////////////////////////////////////////////
//  FETCH METHODS FOR AR PROCESSING
/////////////////////////////////////////////////////
//From forwarder main thread to fetch thread:
void Forwarder::process_fetch(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_fetch function."; 
    //  If message_type is FETCH_END_READOUT,
    //  Make dir using image_id as name under work_dir
    //  Fetch data from DAQ or copy from local drive
    //  Send message to Format thread with image_id as msg_type FORMAT_END_READOUT

    string type_msg = n["MSG_TYPE"].as<string>();
    int retval = 0;

    if (type_msg == "FETCH_END_READOUT") {
      // For raft in raft_list:
      //   send raft and associated ccd list from raft_ccd_list to fetch_readout_image()
      //   ccd_list *could* be 'all', or a subset
      //   fetch_readout_image() should determine which boards (sources) 
      //   are needed to be read for ccd list
      //   The board list should be iterated through.
      //   after each board is read, the appropriate ccds on that board should be split out
      //   This could be done with map with key being board, and val being 
      //   a vector of which CCDs should be pulled

      string image_id = n["IMAGE_ID"].as<string>();
      vector<string> vec_rafts = this->img_to_raft_list[image_id];
      vector<vector<string> > vec_ccds = this->img_to_raft_ccd_list[image_id];
      vector<string> vec;
      ostringstream dir_prefix;
      dir_prefix << this->Work_Dir << "/" << image_id;
      for (int i = 0; i < vec_rafts.size(); i++) {
          vec.clear();
          vec = vec_ccds[i];
          //for (int j = 0; j < this->img_to_raft_ccd_list[i].size(); j++) {
          for (int j = 0; j < vec.size(); j++) {
              ostringstream cmd;
              ostringstream filepath;
              filepath << dir_prefix.str() << "/" \
                       << vec_rafts[i] << "/" \
                       << vec[j];
              cmd << "mkdir -p " << filepath.str();
              const std::string tmpstr = cmd.str();
              const char* cmdstr = tmpstr.c_str();
              system(cmdstr);
          }
      }

      LOGGER(my_logger::get(), debug) << "Created directories for image segments."; 


      retval = this->fetch_readout_image(image_id, dir_prefix.str());

      if(retval == 1) {
           ostringstream desc;
           desc << "Forwarder Fetch Error: Found no image in Catalog for " \
                << image_id << ". Bailing from Readout." << endl;
           this->send_telemetry(1, desc.str());
           this->readout_img_ids.erase(image_id); 
           return;
       }
       if(retval == 2) {
           ostringstream desc;
           desc << "Forwarder Fetch Error: No data slices available for " \
                << image_id << ". Bailing from Readout." << endl;
           this->send_telemetry(2, desc.str());
           this->readout_img_ids.erase(image_id); 
           return;
       }

      // Readout was a good one, so mark img_id as done
      this->readout_img_ids[image_id]["READOUT"] = "yes";

      string new_msg_type = "FORMAT_END_READOUT";
      ostringstream msg;
      msg << "{MSG_TYPE: " << new_msg_type
              << ", IMAGE_ID: " << image_id << "}";
      this->fetch_pub->publish_message(this->format_consume_queue, msg.str());
      LOGGER(my_logger::get(), debug) << "FORMAT_END_READOUT is sent to: " \
                                      << this->format_consume_queue; 
      LOGGER(my_logger::get(), debug) << "Message is: " << msg.str(); 

      return;
    }
}


int Forwarder::fetch_readout_image(string image_id, string dir_prefix) {
    LOGGER(my_logger::get(), debug) << "Entering fetch_readout_image function."; 
  // Iterate through raft_list
  // Foreman divide_work() method might have sent more than one raft,
  // so here we act upon one raft at a time.
  // The ccd_list is a vector that holds the ccds desired from this raft.
  // It might have the string 'ALL'...if so, fetch all ccds for this raft.
  int retval = 0;

  for (int i = 0; i < this->visit_raft_list.size(); i++) {
    vector<string> ccd_list = this->visit_ccd_list_by_raft[i];
    retval = fetch_readout_raft(this->visit_raft_list[i], ccd_list, image_id, dir_prefix);
    if(retval > 0)
        return retval;
  }
  return retval;

}

int Forwarder::fetch_readout_raft(string raft, vector<string> ccd_list, string image_id, string dir_prefix) {
    LOGGER(my_logger::get(), debug) << "Entering fetch_readout_raft function."; 
  // put a map together with raft electronic board (source) for key, and ccd_list as value
  map<string, vector<string>> source_boards;
  int retval = 0;
  if (ccd_list[0] == "ALL") {
    source_boards = All_Boards; //All_Boards is a class visible map
  }
  else {
    for (int i = 0; i < ccd_list.size(); i++) {
      int brd = Board_Layout[ccd_list[i]]; //Board_Layout is a class visible map
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
  retval = this->fetch_reassemble_raft_image(raft, source_boards, image_id, dir_prefix);

}

int Forwarder::fetch_reassemble_raft_image(string raft, \
                                           map<string,vector<string> > source_boards, \
                                           string image_id, \
                                           string dir_prefix) {

    LOGGER(my_logger::get(), debug) << "Entering fetch_reassemble_raft_image function."; 

    int retval = 0;

    // This tmp code checks for the existence of the image name in the DAQ catalog.
    if ((this->check_for_image_existence(image_id)) == 0) {
        cout << "Found an image that exists in Catalog. Fetching " << image_id << " now." << endl;
        retval = 0;
    }
    else {
        cout << "ALERT - ALERT" << endl;
        cout << "Found no image in Catalog for " << image_id << ". Bailing from Readout." << endl;
        ostringstream desc;
        desc << "ALERT - Found no image in Catalog for " << image_id \
             << ". Bailing from Readout." << endl;
        return(1);
    }

    IMS::Store store(raft.c_str()); //DAQ Partitions must be set up to reflect DM name for a raft,
                                    // such as raft01, raft13, etc.

    IMS::Image image(image_id.c_str(), store);

    DAQ::LocationSet sources = image.sources();

    DAQ::Location location;

    int board = 0; // Only way we know how to access a board is by its integer id.


#ifdef METRIX
    auto start = std::chrono::system_clock::now();
    std::time_t start_time = std::chrono::system_clock::to_time_t(start);
    std::cout << "Started raft fetch at " << std::ctime(&start_time) << endl;
    LOGGER(my_logger::get(), debug) << "Started raft fetch at " << std::ctime(&start_time) << endl; 
#endif

    //The loop below processes each raft board (an individual source) one at a time.
    //In order to avoid boards that do not have desired CCDs on them, we check within
    //this loop; if board is not needed, we skip processing it. This is done by
    //converting the board counter to a string, and checking within the source_boards map
    //for a key representing the current board. If it exists, send board(location) to
    //reassemble process

    while(sources.remove(location)) {
        string board_str = std::to_string(board);

        // Check here if bool val is_naxis_set is false...if so,
        // pull register InstructionList info from current source, and
        // set this.naxis1 and this.naxis2.
        //
        // otherwise if true, skip register metadata and use current vals
        if (!is_naxis_set) {
            this->get_register_metadata(location, image);
        }

        // If current board source is in the source_boards map
        // that we put together in the preceeding method...
        if(source_boards.count(board_str)) { 
            std::vector<string> ccds_for_board;
            for (auto ii : source_boards[board_str]) {
                ccds_for_board.push_back(ii);
            }
            retval = this->fetch_reassemble_process(raft, image_id, location, image, \
                                                    ccds_for_board, dir_prefix);
            if(retval > 0)
                return retval;
        }
        board++;
    }

#ifdef METRIX
    auto end = std::chrono::system_clock::now();
    std::chrono::duration<double> elapsed_seconds = end-start;
    std::time_t end_time = std::chrono::system_clock::to_time_t(end);

    std::cout << "Finished raft fetch at " << std::ctime(&end_time)
            << "elapsed time: " << elapsed_seconds.count() << "s\n";
    LOGGER(my_logger::get(), debug) << "Finished raft fetch at " << std::ctime(&end_time) \
                                    << "elapsed time: " << elapsed_seconds.count() << "s\n";
#endif
    return retval;
}


// Above, the source boards are iterated through one at a time.
// If the requested raft/ccd(s) can be found within the current board, the needed CCD list
// for the current board is sent to this method along with the board location.
// These two args are used to extract the correct data.
// The other two args (raft and image_id) are used in constructing the output filename
//
// First, determine the number of CCDs in the ccds_for_board vector arg.
// the number of ccds + the name of each CCD in the vector will tell us how to decode the slice.
//////////////////////////////////////////////////////////////////////////////////////////////////
int Forwarder::fetch_reassemble_process(std::string raft, \
                                        string image_id, \
                                        const DAQ::Location& location, \
                                        const IMS::Image& image, \
                                        std::vector<string> ccds_for_board, \
                                        string dir_prefix) {
    int retval = 0;

    LOGGER(my_logger::get(), debug) << "Entering fetch_reassemble_process function."; 

    IMS::Source source(location, image);

    IMS::Science slice(source);

    if(!slice) return(2);

    // Set up filehandles in Ramdisk work areafor this board. There must be 
    // a separate filehandle set for each CCD to be fetched. CCDs to be fetched 
    // are listed in the ccds_for_board vector. Each CCD
    // will then have a set of 16 filehandles...one filehandle for each amp segment.

    uint64_t pixel = 0;
    uint64_t total_stripes = 0;
    uint64_t pixel_errors = 0;

    //These are for determining if we should skip writing a CCD or not
    bool do_ccd0 = false;
    bool do_ccd1 = false;
    bool do_ccd2 = false;

    // Used when sending image array ready msg to format process
    std::map<string, string> ccd0_map;
    std::map<string, string> ccd1_map;
    std::map<string, string> ccd2_map;
    std::ostringstream ccd0_path;
    std::ostringstream ccd1_path;
    std::ostringstream ccd2_path;

    std::vector<std::ofstream*> FH0;
    std::vector<std::ofstream*> FH1;
    std::vector<std::ofstream*> FH2;

    // Set up file handles for each amp segment per CCD...
    for (int x = 0; x < ccds_for_board.size(); x++) {

        if (string(1, ccds_for_board[x][0]) == "0") {
            do_ccd0 = true;
            this->fetch_set_up_filehandles(FH0, image_id, raft, ccds_for_board[x], dir_prefix);
            ccd0_path << dir_prefix << "/" << raft << "/" << ccds_for_board[x];
            ccd0_map.insert(pair<string,string>("raft",raft));
            ccd0_map.insert(pair<string,string>("ccd",ccds_for_board[x]));
            ccd0_map.insert(pair<string,string>("path",ccd0_path.str()));
        }

        if (string(1, ccds_for_board[x][0]) == "1") {
            do_ccd1 = true;
            this->fetch_set_up_filehandles(FH1, image_id, raft, ccds_for_board[x], dir_prefix);
            ccd1_path << dir_prefix << "/" << raft << "/" << ccds_for_board[x];
            ccd1_map.insert(pair<string,string>("raft",raft));
            ccd1_map.insert(pair<string,string>("ccd",ccds_for_board[x]));
            ccd1_map.insert(pair<string,string>("path",ccd1_path.str()));
        }

        if (string(1, ccds_for_board[x][0]) == "2") {
            do_ccd2 = true;
            this->fetch_set_up_filehandles(FH2, image_id, raft, ccds_for_board[x], dir_prefix);
            ccd2_path << dir_prefix << "/" << raft << "/" << ccds_for_board[x];
            ccd2_map.insert(pair<string,string>("raft",raft));
            ccd2_map.insert(pair<string,string>("ccd",ccds_for_board[x]));
            ccd2_map.insert(pair<string,string>("path",ccd2_path.str()));
        }
    }

    do {
        total_stripes += slice.stripes();
        IMS::Stripe* ccd0 = new IMS::Stripe [slice.stripes()];
        IMS::Stripe* ccd1 = new IMS::Stripe [slice.stripes()];
        IMS::Stripe* ccd2 = new IMS::Stripe [slice.stripes()];

        slice.decode012(ccd0, ccd1, ccd2);
        int num1, num2, num3;

        //////////////////////////////////////////////
        //  NOTICE: Inside these three loops, ccd2 and ccd0 are swapped on purpose

        for(int s=0; s<slice.stripes(); ++s) {

            for(int amp=0; amp<N_AMPS; ++amp) {
                if (do_ccd0) {
                    int32_t X = PIX_MASK ^ ((ccd2[s].segment[amp]));
                    FH0[amp]->write(reinterpret_cast<const char *>(&X), 4); //32 bits...
                }
            }

            for(int amp=0; amp<N_AMPS; ++amp) {
                if (do_ccd1) {
                    int32_t X = PIX_MASK ^ ((ccd1[s].segment[amp]));
                    FH1[amp]->write(reinterpret_cast<const char *>(&X), 4); //32 bits...
                }
            }

            for(int amp=0; amp<N_AMPS; ++amp) {
                if (do_ccd2) {
                    int32_t X = PIX_MASK ^ ((ccd0[s].segment[amp]));
                    FH2[amp]->write(reinterpret_cast<const char *>(&X), 4); //32 bits...
                }
            }
        }
        delete [] ccd0;
        delete [] ccd1;
        delete [] ccd2;

    } while(slice.advance());


    if (do_ccd0) {
        this->fetch_close_filehandles(FH0);
        //this->img_to_raft_ccd_pair[image_id][make_pair(ccd0_map["raft"], \
        //                                               ccd0_map["ccd"]]) = ccd0_map["path"];
        // Add entry to tracking map 
        pair<string,string> ccd0_pair (ccd0_map["raft"],ccd0_map["ccd"]);
        pair<string,pair<string,string> > map_entry (image_id,ccd0_pair);
        this->img_to_raft_ccd_pair[map_entry] = ccd0_map["path"];
        string new_msg_type = "FORMAT_END_READOUT";
        ostringstream msg;
        msg << "{MSG_TYPE: " << new_msg_type
            << ", IMAGE_ID: " << image_id
            << ", RAFT: " << ccd0_map["raft"]
            << ", CCD: " << ccd0_map["ccd"]
            << ", PATH: " << ccd0_map["path"] << "}";
        this->fetch_pub->publish_message(this->format_consume_queue, msg.str());
    }
    if (do_ccd1) {
        this->fetch_close_filehandles(FH1);
        //this->img_to_raft_ccd_pair[image_id][make_pair(ccd1_map["raft"], \
        //                                               ccd1_map["ccd"]]) = ccd1_map["path"];
        // Add entry to tracking map 
        pair<string,string> ccd1_pair (ccd1_map["raft"],ccd1_map["ccd"]);
        pair<string,pair<string,string> > map_entry (image_id,ccd1_pair);
        this->img_to_raft_ccd_pair[map_entry] = ccd1_map["path"];
        string new_msg_type = "FORMAT_END_READOUT";
        ostringstream msg;
        msg << "{MSG_TYPE: " << new_msg_type
            << ", IMAGE_ID: " << image_id
            << ", RAFT: " << ccd1_map["raft"]
            << ", CCD: " << ccd1_map["ccd"]
            << ", PATH: " << ccd1_map["path"] << "}";
        this->fetch_pub->publish_message(this->format_consume_queue, msg.str());
    }
    if (do_ccd2) {
        this->fetch_close_filehandles(FH2);
        //this->img_to_raft_ccd_pair[image_id][make_pair(ccd2_map["raft"], \
        //                                               ccd2_map["ccd"]]) = ccd2_map["path"];
       
        // Add entry to tracking map 
        pair<string,string> ccd2_pair (ccd2_map["raft"],ccd2_map["ccd"]);
        pair<string,pair<string,string> > map_entry (image_id,ccd2_pair);
        this->img_to_raft_ccd_pair[map_entry] = ccd2_map["path"];
        //this->img_to_raft_ccd_pair.insert(pair<string,pair<string,string>(ccd2_map["raft"], \
        //                                               ccd2_map["ccd"])>)) = ccd2_map["path"];
        string new_msg_type = "FORMAT_END_READOUT";
        ostringstream msg;
        msg << "{MSG_TYPE: " << new_msg_type
            << ", IMAGE_ID: " << image_id
            << ", RAFT: " << ccd2_map["raft"]
            << ", CCD: " << ccd2_map["ccd"]
            << ", PATH: " << ccd2_map["path"] << "}";
        this->fetch_pub->publish_message(this->format_consume_queue, msg.str());
    }

    return retval;

}
// This method builds file handle vectors in a RAMDISK.
// The files are essentially dynamically named arrays in memory, and very fast.
void Forwarder::fetch_set_up_filehandles( std::vector<std::ofstream*> &fh_set, 
                                          string image_id, string raft, 
                                          string ccd, string dir_prefix){
    LOGGER(my_logger::get(), debug) << "Entering fetch_set_up_filehandles function."; 

    std::ostringstream full_dir_prefix;
    full_dir_prefix << dir_prefix << "/" << raft << "/" << ccd;

    for (int i=0; i < 16; i++) {
        std::ostringstream fns;
        fns << full_dir_prefix.str() << "/" \
                          << image_id \
                          << "--" << raft \
                          << "-ccd." << ccd \
                          << "_segment." << this->Newest_Segment_Names[i];

        std::ofstream * fh = new std::ofstream(fns.str(), std::ios::out | std::ios::binary );
        fh_set.push_back(fh); 
  }
}

void Forwarder::fetch_close_filehandles(std::vector<std::ofstream*> &fh_set) {
    LOGGER(my_logger::get(), debug) << "Entering fetch_close_filehandles function.";

  for (int i = 0; i < 16; i++) {
    fh_set[i]->close();
  }
    LOGGER(my_logger::get(), debug) << "Finished closing file handlers for image segments."; 
}


int Forwarder::check_for_image_existence(string image_id) {
  int x;
  std::string line = "./ims.sh ";
  line += image_id;
  x = system(line.c_str());
  return x;
}


void Forwarder::get_register_metadata(const DAQ::Location& location, const IMS::Image& image) {

        // Here are the values and associated indexes
        // into the InstructionList returned by source.registers().
        // These index values are used in the lookup() call below.
        // They are subject to change...
        // REG_READ_ROWS = 0,
        // REG_READ_COLS = 1,
        // REG_PRE_ROWS = 2,
        // REG_PRE_COLS = 3,
        // REG_POST_ROWS = 4,
        // REG_POST_COLS = 5,
        // REG_READ_COLS2 = 6,
        // REG_OVER_ROWS = 7,
        // REG_OVER_COLS = 8,
        // NUM_REGISTERS = 9;

    IMS::Source source(location, image);

    const RMS::InstructionList *reglist = source.registers();

    // READ_ROWS + OVER_ROWS
    const RMS::Instruction *inst0 = reglist->lookup(0);
    uint32_t operand0 = inst0->operand();

    const RMS::Instruction *inst7 = reglist->lookup(7);
    uint32_t operand7 = inst7->operand();

    this->Naxis_2 = operand0 + operand7;

    // READ_COLS + READ_COLS2 + OVER_COLS
    const RMS::Instruction *inst1 = reglist->lookup(1);
    uint32_t operand1 = inst1->operand();

    const RMS::Instruction *inst6 = reglist->lookup(6);
    uint32_t operand6 = inst6->operand();

    const RMS::Instruction *inst8 = reglist->lookup(8);
    uint32_t operand8 = inst8->operand();

    this->Naxis_1 = operand1 + operand6 + operand8;

    this->is_naxis_set = true;

}


void Forwarder::process_fetch_ack(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_fetch_ack function.";
    cout << "fetch ack being processed" << endl;
    return;
}

void Forwarder::process_fetch_health_check(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_fetch_health_check function.";
    cout << "Send helth check to just fetch queue" << endl;
    return;
}

void Forwarder::process_fetch_health_check_ack(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_fetch_health_check_ack function.";
    cout << "Health check ack for fetch" << endl;
    return;
}

void Forwarder::process_format(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_format function."; 
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
    LOGGER(my_logger::get(), debug) << "FORWARD_TAKE_IMAGES_DONE is sent to: " << this->forward_consume_queue; 
    LOGGER(my_logger::get(), debug) << "Message is: " << msg; 
      return;
    }
    return;
}

void Forwarder::process_forward(Node n) { 
    LOGGER(my_logger::get(), debug) << "Entering process_forward function.";
} 

void Forwarder::process_format_ack(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_format_ack function.";
    return;
}

void Forwarder::process_format_health_check(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_format_health_check function.";
    return;
}

void Forwarder::process_format_health_check_ack(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_format_health_check_ack function.";
    return;
}

void Forwarder::process_forward_ack(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_forward_ack function.";
  return;
}

void Forwarder::process_forward_health_check(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_forward_health_check function.";
}

void Forwarder::process_forward_health_check_ack(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_forward_health_check_ack function.";
  return;
}

////////////////////////////////////////////////////////////////////////////////
// FORMAT THREAD
////////////////////////////////////////////////////////////////////////////////
void Forwarder::process_header_ready(Node n) { 
    LOGGER(my_logger::get(), debug) << "Entering process_header_ready function."; 
    try { 
        string main_header_dir = this->Work_Dir + "/header"; 
        const int dir = mkdir(main_header_dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR); 
        if (dir == -1 && errno != 17) { 
            throw L1CannotCreateDirError("In process_header_ready, forwarder cannot create directory in: " + main_header_dir); 
        } 
        LOGGER(my_logger::get(), debug) << "Creating header directory."; 
        LOGGER(my_logger::get(), debug) << "Header directory to store file is " << main_header_dir.c_str(); 

        if (!n["FILENAME"]) { 
            throw L1YamlKeyError("In process_header_ready, forwarder cannot find message params: FILENAME"); 
        } 

        string reply_queue = n["REPLY_QUEUE"].as<string>();
        string ack_id = n["ACK_ID"].as<string>();
        string message_type = "AT_FWDR_HEADER_READY_ACK";
        string ack_bool = "True";

        ostringstream message;
        message << "{ MSG_TYPE: " << message_type
                << ", COMPONENT: " << this->Component
                << ", ACK_ID: " << ack_id
                << ", ACK_BOOL: " << ack_bool << "}";

        // Inform AuxDevice message was received.
        FWDR_pub->publish_message(reply_queue, message.str());
        LOGGER(my_logger::get(), debug) << "AT_FWDR_HEADER_READY_ACK is sent to: " << reply_queue; 
        LOGGER(my_logger::get(), debug) << "Message is: " << message; 

        string path = n["FILENAME"].as<string>(); 
        string img_id = n["IMAGE_ID"].as<string>(); 
        int img_idx = path.find_last_of("/"); 
        /** 
        int dot_idx = path.find_last_of("."); 
        int num_char = dot_idx - (img_idx + 1); // offset +1
        string img_id = path.substr(img_idx + 1, num_char); 
        */

        string sub_dir = main_header_dir + "/" + img_id; 
        const int dir_cmd = mkdir(sub_dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR);  
        LOGGER(my_logger::get(), debug) << "Created sub header directory for image id at " << sub_dir.c_str(); 
        if (dir_cmd == -1 && errno != 17) { 
            throw L1CannotCreateDirError("In process_header_ready, forwarder cannot create sub_directory in: " + sub_dir); 
        } 
        LOGGER(my_logger::get(), debug) << "Created sub header directory for image id at " << sub_dir.c_str(); 

        // scp -i ~/.ssh/from_efd felipe@141.142.23x.xxx:/tmp/header/IMG_ID.header to /tmp/header/IMG_ID/IMG_ID.header
        ostringstream cp_cmd; 
	/** 
        cp_cmd << "scp -i ~/.ssh/from_efd "
               << path
               << " " 
               << sub_dir
               << "/"; 
	*/ 
	cp_cmd << "wget -P " << sub_dir << "/ " << path; 
        int scp_cmd = system(cp_cmd.str().c_str()); 
        LOGGER(my_logger::get(), debug) << "Copying header file from efd and command is " << cp_cmd.str(); 

	/** 
	ostringstream move_cmd; 
	int move_idx = path.find_last_of("/"); 
	int dot_idx = path.find_last_of("."); 
        int num_char = dot_idx - (move_idx + 1); // offset +1
	string move_str = path.substr(move_idx + 1, num_char); 

	move_cmd << "mv " << move_str << " " << sub_dir << "/"; 
	cout << "[STATUS] " << move_cmd.str() << endl; 
	int move_cmd_exec = system(move_cmd.str().c_str()); 
	cout << "Moved file to " << sub_dir << endl; 
	*/ 

        if (scp_cmd == 256) { 
            throw L1CannotCopyFileError("In process_header_ready, forwarder cannot copy file: " + cp_cmd.str()); 
        } 
        LOGGER(my_logger::get(), debug) << "Copied header file from efd."; 

        string img_idx_wheader = path.substr(img_idx + 1);  
        string header_path = sub_dir + "/" + img_idx_wheader;
        LOGGER(my_logger::get(), debug) << "Header path for processing is " << header_path; 

        Emitter msg; 
        msg << BeginMap; 
        msg << Key << "MSG_TYPE" << Value << "FORMAT_HEADER_READY"; 
        msg << Key << "IMAGE_ID" << Value << img_id; 
        msg << Key << "FILENAME" << Value << header_path; 
        msg << EndMap; 
        FWDR_to_format_pub->publish_message(this->format_consume_queue, msg.c_str()); 
        LOGGER(my_logger::get(), debug) << "FORMAT_HEADRE_READY is sent to: " << this->format_consume_queue; 
        // FIXXX LOGGER(my_logger::get(), debug) << "Message is: " << msg; 
    } 
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        LOGGER(my_logger::get(), critical) << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (L1CannotCreateDirError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 20; 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        LOGGER(my_logger::get(), critical) << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (L1CannotCopyFileError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 21; 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        LOGGER(my_logger::get(), critical) << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        cerr << e.what() << endl; 
    } 
} 

////////////////////////////////////////////////////////////////////////////////
// F@
////////////////////////////////////////////////////////////////////////////////

void Forwarder::format_process_end_readout(Node node) { 
    LOGGER(my_logger::get(), debug) << "Entering format_process_end_readout function."; 
    try { 
        string image_id = node["IMAGE_ID"].as<string>(); 
        //this->readout_img_ids.push_back(image_id); 
        this->format_look_for_work(image_id); 
        LOGGER(my_logger::get(), debug) << "Looking header file for current ImageID " << image_id; 
        LOGGER(my_logger::get(), debug) << "Looking work for current Readout pixels is complete."; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_get_header(Node node) { 
    LOGGER(my_logger::get(), debug) << "Entering format_get_header function."; 
    try { 
        string image_id = node["IMAGE_ID"].as<string>(); 
        string filename = node["FILENAME"].as<string>(); 
        LOGGER(my_logger::get(), debug) << "Got ImageID " << image_id << " and Filename " << filename << " for processing.";
        this->header_info_dict[image_id] = filename; 
        this->format_look_for_work(image_id); 
        LOGGER(my_logger::get(), debug) << "Looking work for current Header file is complete."; 
    } 
    catch (exception& e) { 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_assemble_img(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering format_assemble_img function."; 
    try { 
        string img_id = n["IMAGE_ID"].as<string>(); 
        string header_path = n["HEADER_PATH"].as<string>(); 
        string binary_path = n["BINARY_PATH"].as<string>(); 

        // create dir  /mnt/ram/FITS/IMG_10
        string fits_dir = Work_Dir + "/FITS"; 
        const int dir = mkdir(fits_dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR); 
        LOGGER(my_logger::get(), debug) << "Created directory " << fits_dir << " for assembling images."; 
        format_write_img(img_id, header_path, binary_path);
        LOGGER(my_logger::get(), debug) << "Start formatting ..."; 
    } 
    catch (exception& e) { 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        cerr << e.what() << endl; 
    } 
}

void Forwarder::format_write_img(string img_id, string header_file_path, string binary_file_path) { 
    LOGGER(my_logger::get(), debug) << "Entering format_write_img function."; 
    try { 
        long len = NAXIS1 * NAXIS2;
        int bitpix = LONG_IMG; 
        long naxis = 2;
        long naxes[2] = { NAXIS1, NAXIS2 }; 
        long fpixel = 1; 
        int status = 0; 
        int hdunum = 2;
        int nkeys; 
        char card[FLEN_CARD]; 
        fitsfile *iptr, *optr; 

        // /mnt/ram/IMG_31
        string header_path = header_file_path;
        string destination = Work_Dir + "/FITS/" + img_id + ".fits";
        LOGGER(my_logger::get(), debug) << "Image file path is " << binary_file_path; 
        LOGGER(my_logger::get(), debug) << "Header file path is " << header_path; 
        LOGGER(my_logger::get(), debug) << "Destination file path is " << destination; 

        if (FILE *file = fopen(destination.c_str(), "r")) { 
            LOGGER(my_logger::get(), debug) << "Fits file already exists. So deleting ..."; 
            // file exists
            fclose(file); 
            ostringstream rm_cmd; 
            rm_cmd << "rm " << destination; 
            
            LOGGER(my_logger::get(), debug) << "Delete command is " << rm_cmd.str(); 
            system(rm_cmd.str().c_str()); 
            LOGGER(my_logger::get(), debug) << "Already existed fits file is deleted from directory."; 
        } 

        LOGGER(my_logger::get(), debug) << "Start to process fits files with cfitsio."; 
        fits_open_file(&iptr, header_path.c_str(), READONLY, &status); 
        fits_create_file(&optr, destination.c_str(), &status); 
        fits_copy_hdu(iptr, optr, 0, &status); 
        LOGGER(my_logger::get(), debug) << "Finished copying primary hdu to file."; 

        vector<string> file_names = format_list_files(binary_file_path); 
        vector<string>::iterator it; 
        vector<string> exclude_keywords = {"BITPIX", "NAXIS"}; 
        vector<string>::iterator eit; 
	while (fits_movabs_hdu(iptr, hdunum, NULL, &status) == 0) {
	    fitsfile *pix_file_ptr; 
            string segment_name; 
            int *img_buffer = new int[len];
            if (fits_create_img(optr, bitpix, naxis, naxes, &status)){
                LOGGER(my_logger::get(), critical) << "Fits_create_img error. Error code is: " << status; 
            }
            fits_get_hdrspace(iptr, &nkeys, NULL, &status); 
            for (int i = 1; i <= nkeys; i++) { 
                fits_read_record(iptr, i, card, &status); 
	        string card_str = string(card); 
                if (card_str.find("BITPIX") == 0) {} 
                else if (card_str.find("NAXIS") == 0) {} 
                else if (card_str.find("PCOUNT") == 0) {} 
                else if (card_str.find("GCOUNT") == 0) {} 
                else if (card_str.find("XTENSION") == 0) {} 
                else if (card_str.find("EXTNAME") == 0) { 
		    fits_write_record(optr, card, &status); 
		    segment_name = card_str; 
		} 
                else { 
		    fits_write_record(optr, card, &status); 
                } 
            }
	
	    if (!segment_name.empty()) { 
                size_t find_digits = segment_name.find_last_of("Segment"); 	
                if (find_digits != string::npos) { 
                    string digits = segment_name.substr(find_digits+1, 2); 

                    // find two ending digits in binary pixel 
                    size_t dot = file_names[0].find_last_of("."); 
                    string prefix = file_names[0].substr(0, dot+1); 
                    string search_string = prefix + digits; 
                    vector<string>::iterator bit = find(file_names.begin(), file_names.end(), search_string); 
                    if (bit != file_names.end()){ 
                        // do assembly 
                        string img_segment_name = binary_file_path + "/" + *bit 
                                                  + "[jL" + STRING(NAXIS1) 
                                                  + "," + STRING(NAXIS2) + "]"; 
                        if (fits_open_file(&pix_file_ptr, img_segment_name.c_str(), READONLY, &status)) { 
                            LOGGER(my_logger::get(), critical) << "Fits_open_file error " << status << endl; 
                        }  
                        if (fits_read_img(pix_file_ptr, TINT, 1, len, NULL, img_buffer, 0, &status)){
                            LOGGER(my_logger::get(), critical) << "Fits_read_imge error " << status << endl; 
                        }
                        if (fits_write_img(optr, TINT, 1, len, img_buffer, &status)){
                            LOGGER(my_logger::get(), critical) << "Fits_write_img error " << status << endl; 
                        } 

                        // clean up 
                        fits_close_file(pix_file_ptr, &status); 
                        delete[] img_buffer; 
                    } 
                    else { 
                        cout << "Did not find corresponding binary file" << endl; 
                    }  
                }  
	    } 
	    else { 
                cout << "Cannot find Extname keyword in header file" << endl; 
            } 
            hdunum++;
	} 
        fits_close_file(iptr, &status); 
        fits_close_file(optr, &status); 
        LOGGER(my_logger::get(), debug) << "Formatting image segments into fits file is completed."; 
        format_send_completed_msg(img_id);
        LOGGER(my_logger::get(), debug) << "Sending format complete message to forward thread."; 
    } 
    catch (exception& e) { 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        cerr << e.what() << endl; 
    } 
} 

vector<string> Forwarder::format_list_files(string path) { 
    LOGGER(my_logger::get(), debug) << "Entering format_list_files function."; 
    try { 
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
        LOGGER(my_logger::get() , debug) << "Added file list for further processing."; 
        return file_names; 
    } 
    catch (exception& e) { 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_send_completed_msg(string image_id) { 
    LOGGER(my_logger::get(), debug) << "Entering format_send_completed_msg function.";
    try { 
        Emitter msg; 
        msg << BeginMap; 
        msg << Key << "MSG_TYPE" << Value << "FORWARD_END_READOUT"; 
        msg << Key << "IMAGE_ID" << Value << image_id; 
        msg << EndMap; 
        fmt_pub->publish_message(this->forward_consume_queue, msg.c_str()); 
        LOGGER(my_logger::get(), debug) << "FORWARD_END_READOUT is sent to: " << this->forward_consume_queue; 
        // FIXXX LOGGER(my_logger::get(), debug) << "Message is: " << msg; 
    } 
    catch (exception& e) { 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        cerr << e.what() << endl; 
    } 
} 
///////////////////////////////////////////////////////////////////////////

string Forwarder::format_get_binary_path(string image_id) { 
    /**
     * Returns the path to the binary image segments for formatter. If it exists
     * in the raft_ccd_to_pair dictionary, returns the path string or else empty string.
     */ 
    string binary_path; 
    map<pair<string, pair<string, string>>, string>::iterator it; 
    for (it = this->img_to_raft_ccd_pair.begin(); it != this->img_to_raft_ccd_pair.end(); it++) { 
        pair<string, pair<string, string>> imgid_raft_ccd = it->first; 
        string img_id = imgid_raft_ccd.first; 
        if (img_id == image_id) { 
//////// Shouldn't this build the key with make_pair and then get path from overall map?
            binary_path = it->second;          

            // delete the iterator
            img_to_raft_ccd_pair.erase(it); 
            break; 
        } 
    } 
    return binary_path; 
} 

void Forwarder::format_look_for_work(string image_id) { 
    /**
     * Triggered when HEADER_READY or FORMAT_END_READOUT is 
     * issued. When either method calls, this method checks if there is an entry in 
     * img_to_raft_ccd_pair and header_info_dict and do the work.
     */ 
    LOGGER(my_logger::get(), debug) << "Entering format_look_for_work function."; 
    try { 
        map<string, string>::iterator header_it = this->header_info_dict.find(image_id); 
        string binary_path = format_get_binary_path(image_id); 
        LOGGER(my_logger::get(), debug) << "Found the following binary path: " << binary_path;
        if (header_it != this->header_info_dict.end() && !binary_path.empty()) { 
            LOGGER(my_logger::get(), debug) << "Found both header and binary paths to start assembling."; 
            Node n; 
            n["IMAGE_ID"] = image_id; 
            n["HEADER_PATH"] = header_it->second; 
            n["BINARY_PATH"] = binary_path; 
            format_assemble_img(n); 
        } 
        /** 

        // Set up vector of outer map keys...
        vector<string> keys;
        map <string, map <string, string> >::iterator it = this->readout_img_ids.begin();
        for( ; it != readout_img_ids.end(); ++it) {
            keys.push_back(it->first);
        }

        std::vector<string>::iterator iit;
        map<string, string>::iterator mit;  
        map<string, string>::iterator tid; 
        // if there are elements in both keys and header_info vectors...
        // we check if the current iterator img_id value has been readout yet.
        // if so, we get the header name, delete it from header_info, and process.
        // readout_img_ids entry stays around as forward process will use it.
        if (keys.size() != 0 && this->header_info_dict.size() != 0) { 
            for (iit = keys.begin(); iit != keys.end(); ) { 
                string img_id = *iit; 
                mit = this->header_info_dict.find(img_id); 
                if ((this->readout_img_ids[img_id]["READOUT"] == "yes") \
                   && mit != this->header_info_dict.end()) { 
                    //this->readout_img_ids.erase(it); 
                    string header_filename = this->header_info_dict[img_id]; 
                    this->header_info_dict.erase(mit); 

                    // do the work 
                    Node n; 
                    n["IMAGE_ID"] = img_id; 
                    n["HEADER"] = header_filename; 
                    format_assemble_img(n); 
                } 
                else iit++; 
            } 
        } 
        else if (this->readout_img_ids.size() == 0 || this->header_info_dict.size() == 0) { 
            LOGGER(my_logger::get(), debug) << "No img data from DAQ yet. Waiting to process."; 
            return; 
        } 
        */ 
    } 
    catch (exception& e) { 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        cerr << e.what() << endl; 
    } 
// ADD RESULT SET CODE HERE...
} 

///////////////////////////////////////////////////////////////////////////////
// Forward part 
///////////////////////////////////////////////////////////////////////////////

void Forwarder::forward_process_end_readout(Node n) { 
    
    LOGGER(my_logger::get(), debug) << "Entering forward_process_end_readout function."; 

    string new_csum = "0";
    try { 
        string img_id = n["IMAGE_ID"].as<string>(); 
        string img_path = this->Work_Dir + "/FITS/" + img_id + ".fits"; 
        string dest_path = this->Target_Location + "/" + img_id + ".fits"; 
      
        size_t find_at = dest_path.find("@"); 
        ostringstream bbcp_cmd; 
        if (find_at != string::npos) { 
            bbcp_cmd << "bbcp -f -i ~/.ssh/id_rsa ";
        } 
        else { 
            bbcp_cmd << "cp "; 
        } 
        bbcp_cmd << img_path
                 << " " 
                 << dest_path; 

        // If enabled, calculate checksum for verification use at Archive
        if (this->Checksum_Enabled == true) {
            if(this->Checksum_Type == "MD5") {
                new_csum = this->forward_calculate_md5_checksum(img_path);
            }
            else if(this->Checksum_Type == "CRC32") {
                new_csum = this->forward_calculate_crc32_checksum(img_path);
            }
        }

        int bbcp_cmd_status = system(bbcp_cmd.str().c_str()); 
        LOGGER(my_logger::get(), debug) << "Command to copy file is " << bbcp_cmd.str(); 
	LOGGER(my_logger::get(), debug) << "File is copied from " << img_path << " to "<< dest_path; 


        if (bbcp_cmd_status == 256) { 
            throw L1CannotCopyFileError("In forward_process_end_readout, forwarder cannot copy file: " + bbcp_cmd.str()); 
        } 
        this->finished_image_work_list.push_back(img_id);
        this->forward_send_result_set(img_id, dest_path, new_csum);
        LOGGER(my_logger::get(), info) << "READOUT COMPLETE.";

    } 
    catch (L1CannotCopyFileError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 21; 
        // FIXXX Telemetry Here...
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        LOGGER(my_logger::get(), critical) << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        cerr << e.what() << endl; 
    } 
} 


std::string Forwarder::forward_send_result_set(string image_id, string filenames, string checksums) {
    // Get device from xfer_params vars
    // Use device to know where to send end readout and which msg_type to use
    ostringstream msg_type;
    string job_num = this->image_ids_to_jobs_map[image_id]["JOB_NUM"];
    string ack_id = this->image_ids_to_jobs_map[image_id]["ACK_ID"];
    string reply_queue = this->Foreman_Reply_Queue;
    string device_type = this->Device_Type;

    msg_type << device_type << " _FWDR_END_READOUT_ACK ";
    string ack_bool = "True";

    Emitter msg;
    msg << BeginMap;
    msg << Key << "MSG_TYPE" << Value << msg_type;
    msg << Key << "COMPONENT" << Value << this->Component;
    msg << Key << "IMAGE_ID" << Value << image_id;
    msg << Key << "JOB_NUM" << Value << job_num;
    msg << Key << "ACK_ID" << Value << ack_id;
    msg << Key << "ACK_BOOL" << Value << ack_bool;
    msg << Key << "RESULT_SET" << Value << Flow;
        msg << BeginMap;
        msg << Key << "FILENAME_LIST" << Value << Flow << filenames;
        msg << Key << "CHECKSUM_LIST" << Value << Flow << checksums;
        msg << EndMap;
    msg << EndMap;
    cout << "[x] tid msg: " << endl;
    cout << msg.c_str() << endl;

    this->fwd_pub->publish_message(reply_queue, msg.c_str());
    cout << "msg is replied to ..." << reply_queue << endl;
}

std::string Forwarder::forward_calculate_md5_checksum(const string img_path ) {
      FILE *fh;
      long filesize;
      unsigned char *buf;
      unsigned char *md5_result = NULL;
      char csum [32];
      std::string md5_csum;
      std::ostringstream outage;
      std::streamsize const  buffer_size = PRIVATE_BUFFER_SIZE;
      if(this->Checksum_Type == "MD5") {
          FILE *fh;
          long filesize;
          unsigned char *buf;
          unsigned char *md5_result = NULL;

          fh = fopen(img_path.c_str(), "r");
          fseek(fh, 0L, SEEK_END);
          filesize = ftell(fh);
          fseek(fh, 0L, SEEK_SET);
          buf = (unsigned char *)malloc(filesize);
          fread(buf, filesize, 1, fh);
          fclose(fh);

          md5_result = (unsigned char *)malloc(MD5_DIGEST_LENGTH);
          MD5(buf, filesize, md5_result);
          for (int i=0; i < MD5_DIGEST_LENGTH; i++) {
              sprintf(csum, "%02x",  md5_result[i]);
              md5_csum.append(csum);
          }

          for(unsigned int k = 0; k < md5_csum.length(); k++) {
              md5_csum[k] = toupper(md5_csum[k]);
          }


          std::cout << "MD5 Checksum is:  " << md5_csum << "  " <<  std::endl;

          free(md5_result);
          free(buf);
          return md5_csum;
      }
}
std::string Forwarder::forward_calculate_crc32_checksum(const string img_path) {
      std::streamsize const  buffer_size = PRIVATE_BUFFER_SIZE;
      boost::crc_32_type  result;
      std::ifstream  ifs( img_path, std::ios_base::binary );
      if(ifs) {
          do {
              char  buffer[ buffer_size ];
              ifs.read( buffer, buffer_size );
              result.process_bytes( buffer, ifs.gcount() );
          } while(ifs);
      } else {
          std::cerr << "Failed to open file '" << img_path << "'." << std::endl;
      }

      //std::cout << std::hex << std::uppercase << result.checksum() << std::endl;
      std::cout << "CRC32 Checksum is  " << result.checksum() << std::endl;
      std::string csum = std::to_string(result.checksum());
      return csum;
}



void Forwarder::forward_process_take_images_done(Node n) { 
    LOGGER(my_logger::get(), debug) << "Entering forward_process_take_images_done function."; 
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
    LOGGER(my_logger::get(), debug)  << "Published message is " << msg.c_str();
  
    this->fwd_pub->publish_message(reply_queue, msg.c_str());
    LOGGER(my_logger::get(), debug) << "AR_FWDR_TAKE_IMAGES_DONE_ACK is sent to: " << reply_queue; 
    // FIXXX LOGGER(my_logger::get(), debug) << "Message is: " << msg; 
} 

//void Forwarder::forward_process_end_readout_done(Node n) { 
//    cout << "get here" << endl;
//    ostringstream message;
//    string ack_id = n["ACK_ID"].as<string>();
//    string reply_queue = n["REPLY_QUEUE"].as<string>();
//    string msg_type = "AR_FWDR_TAKE_IMAGES_DONE_ACK ";
//    string ack_bool = "True";
// 
//    Emitter msg; 
//    msg << BeginMap; 
//    msg << Key << "MSG_TYPE" << Value << msg_type; 
//    msg << Key << "COMPONENT" << Value << this->Component; 
//    msg << Key << "ACK_ID" << Value << ack_id; 
//    msg << Key << "ACK_BOOL" << Value << ack_bool; 
//    msg << Key << "RESULT_SET" << Value << Flow; 
//        msg << BeginMap; 
//        msg << Key << "FILENAME_LIST" << Value << Flow << finished_image_work_list; 
//        msg << Key << "CHECKSUM_LIST" << Value << Flow << checksum_list;  
//        msg << EndMap; 
//    msg << EndMap; 
//    cout << "[x] tid msg: " << endl; 
//    cout << msg.c_str() << endl;
//  
//    this->fwd_pub->publish_message(reply_queue, msg.c_str());
//    cout << "msg is replied to ..." << reply_queue << endl;
//} 

void Forwarder::send_telemetry(int code, std::string description) {
      Emitter msg;
      msg << BeginMap;
      msg << Key << "MSG_TYPE" << Value << "TELEMETRY";
      msg << Key << "STATUS_CODE" << Value << code;
      msg << Key << "DEVICE" << Value << this->Device_Type;
      msg << Key << "DESCRIPTION" << Value << description;
      msg << EndMap;
      this->fetch_pub->publish_message(this->Telemetry_Queue, msg.c_str());

      return;
}



int main() {
    Forwarder *fwdr = new Forwarder();
    fwdr->run();
    while(1) {
    }
}


