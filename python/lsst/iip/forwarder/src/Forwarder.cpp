#include "Forwarder.h"

BOOST_LOG_INLINE_GLOBAL_LOGGER_DEFAULT(my_logger, src::severity_logger_mt< severity_level >);

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

        //this->WFS_RAFT = root["ATS"]["WFS_RAFT"].as<string>();
        //cout << "Setting WFS_RAFT class var to:  " << this->WFS_RAFT << endl << endl << endl;
    }
    catch (YAML::TypedBadConversion<string>& e) {
        LOGGER(my_logger::get(), critical) << e.what();
        LOGGER(my_logger::get(), critical) << "In ForwarderCfg.yaml, cannot read required elements from this file.";
    }

    // Read L1 config file
    Node L1_config_file;
    try {
        L1_config_file = LoadFile("../../L1SystemCfg.yaml");
        LOGGER(my_logger::get(), debug) << "Reading L1SystemCfg config file."; 
    }
    catch (YAML::BadFile& e) {
        // FIX better catch clause...at LEAST a log message
        LOGGER(my_logger::get(), critical) << "Error reading L1SystemCfg.yaml file.";
        exit(EXIT_FAILURE);
    }

    try {
        Node cdm;
        cdm = config_file["ROOT"];
        if((cdm["ARCHIVE"]["CHECKSUM_ENABLED"].as<string>()) == "yes") {
            this->Checksum_Enabled = true;
            this->Checksum_Type = cdm["ARCHIVE"]["CHECKSUM_TYPE"].as<string>();
        }
        else {
            this->Checksum_Enabled = false;
        }
    }
    catch (YAML::TypedBadConversion<string>& e) {
        LOGGER(my_logger::get(), critical) << e.what();
        LOGGER(my_logger::get(), critical) << "In L1SystemCfg.yaml, cannot read required elements from this file.";
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
    LOGGER(my_logger::get(), debug) << "Consumer broker URL is: " << full_broker_url;
    from_foreman_consumer = new Consumer(full_broker_url.str(), this->consume_queue);

    ostringstream consume_queue1;
    consume_queue1 << this->consume_queue << "_from_fetch";
    from_fetch_consumer = new Consumer(full_broker_url.str(), consume_queue1.str());
    LOGGER(my_logger::get(), debug) << "Consuming from queue: " << consume_queue1;

    ostringstream consume_queue2;
    consume_queue2 << this->consume_queue << "_from_format";
    from_format_consumer = new Consumer(full_broker_url.str(), consume_queue2.str());
    LOGGER(my_logger::get(), debug) << "Consuming from queue: " << consume_queue2;

    ostringstream consume_queue3;
    consume_queue3 << this->consume_queue << "_from_forward";
    ostringstream from_fwd_broker_url;
    from_fwd_broker_url << "amqp://" << this->USER << ":" << this->PASSWD << this->BASE_BROKER_ADDR ;
    from_forward_consumer = new Consumer(full_broker_url.str(), consume_queue3.str());
    LOGGER(my_logger::get(), debug) << "Consumer broker URL is: " << from_fwd_broker_url;
    LOGGER(my_logger::get(), debug) << "Consuming from queue: " << consume_queue3;

    //Consumers for sub-components
    //ostringstream consume_queue;

    ostringstream full_broker_url2;
    full_broker_url2 << "amqp://" << this->FETCH_USER << ":" << this->FETCH_USER_PASSWD << this->BASE_BROKER_ADDR ;
    from_forwarder_to_fetch = new Consumer(full_broker_url.str(), this->fetch_consume_queue);
    LOGGER(my_logger::get(), debug) << "Consumer broker URL is: " << full_broker_url2;
    LOGGER(my_logger::get(), debug) << "Consuming from queue: " << this->fetch_consume_queue;

    ostringstream full_broker_url3;
    full_broker_url3 << "amqp://" << this->FORMAT_USER << ":" << this->FORMAT_USER_PASSWD << this->BASE_BROKER_ADDR;
    from_forwarder_to_format = new Consumer(full_broker_url.str(), this->format_consume_queue);
    LOGGER(my_logger::get(), debug) << "Consumer broker URL is: " << full_broker_url3;
    LOGGER(my_logger::get(), debug) << "Consuming from queue: " << this->format_consume_queue;
    //cout << this->format_consume_queue << endl; 

    ostringstream full_broker_url4;
    full_broker_url4 << "amqp://" << this->FORWARD_USER << ":" << this->FORWARD_USER_PASSWD << this->BASE_BROKER_ADDR ;
    from_forwarder_to_forward = new Consumer(full_broker_url.str(), this->forward_consume_queue);
    LOGGER(my_logger::get(), debug) << "Consumer broker URL is: " << full_broker_url4;
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
    LOGGER(my_logger::get(), debug) << "Health Check request Message, ACK sent to: " << reply_queue << endl;
    LOGGER(my_logger::get(), debug) << "Message sent is: " << message.str() << endl;
    LOGGER(my_logger::get(), info) << "Processing health check message complete."; 
    return;
}

void Forwarder::process_xfer_params(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_xfer_params function."; 
    LOGGER(my_logger::get(), debug) << "Incoming message is: " << n;

    this->Device_Type = "AR";

    Node p = n["XFER_PARAMS"];
    LOGGER(my_logger::get(), debug) << "Incoming xfer_params is: " << p;

    this->visit_raft_list.clear();
    this->visit_raft_list = p["RAFT_LIST"].as<vector<string>>();
    LOGGER(my_logger::get(), debug) << "RAFT_LIST has been assigned to class variable.";

    this->visit_ccd_list_by_raft.clear();
    this->visit_ccd_list_by_raft = p["RAFT_CCD_LIST"].as<std::vector<std::vector<string>>>();
    LOGGER(my_logger::get(), debug) << "RAFT_CCC_LIST has been assigned to class variable.";

    this->Session_ID = n["SESSION_ID"].as<string>();
    LOGGER(my_logger::get(), debug) << "SESSION_ID has been assigned: " << this->Session_ID;

    this->Job_Num = n["JOB_NUM"].as<string>();
    LOGGER(my_logger::get(), debug) << "JOB_NUM has been assigned: " << this->Job_Num;

    this->Target_Location = n["TARGET_LOCATION"].as<string>();
    LOGGER(my_logger::get(), debug) << "TARGET_LOCATION has been assigned: " << this->Target_Location;

    this->Foreman_Reply_Queue = n["REPLY_QUEUE"].as<string>();
    LOGGER(my_logger::get(), debug) << "REPLY_QUEUE has been assigned: " << this->Foreman_Reply_Queue;

    string ack_id = n["ACK_ID"].as<string>();
    LOGGER(my_logger::get(), debug) << "ACK_ID has been assigned: " << ack_id;

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

    FWDR_pub->publish_message(this->Foreman_Reply_Queue, message.str());
    LOGGER(my_logger::get(), debug) << "AR_XFER_PARAMS_ACK is sent to: " << this->Foreman_Reply_Queue; 
    LOGGER(my_logger::get(), debug) << "Message is: " << message.str(); 
    LOGGER(my_logger::get(), info) << "Processing transfer params is complete."; 
    return;
}

void Forwarder::process_at_xfer_params(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_at_xfer_params function."; 
    LOGGER(my_logger::get(), debug) << "Incoming message is: " << n;
    this->Device_Type = "AT";

    Node p = n["XFER_PARAMS"];
    LOGGER(my_logger::get(), debug) << "Incoming xfer_params is: " << p;

    this->visit_raft_list.clear();
    this->visit_raft_list = p["RAFT_LIST"].as<vector<string>>();
    LOGGER(my_logger::get(), debug) << "RAFT_LIST has been assigned to class variable.";

    this->visit_ccd_list_by_raft.clear();
    this->visit_ccd_list_by_raft = p["RAFT_CCD_LIST"].as<std::vector<std::vector<string>>>();
    LOGGER(my_logger::get(), debug) << "RAFT_CCC_LIST has been assigned to class variable.";

    //this->Session_ID = n["SESSION_ID"].as<string>();
    //cout << "After setting SESSION_ID" << endl;

    //this->Job_Num = n["JOB_NUM"].as<string>();
    //cout << "After setting JOB_NUM" << endl;

    this->Target_Location = n["TARGET_LOCATION"].as<string>();
    LOGGER(my_logger::get(), debug) << "TARGET_LOCATION has been assigned: " << this->Target_Location;

    this->Foreman_Reply_Queue = n["REPLY_QUEUE"].as<string>();
    LOGGER(my_logger::get(), debug) << "REPLY_QUEUE has been assigned: " << this->Foreman_Reply_Queue;

    string ack_id = n["ACK_ID"].as<string>();
    LOGGER(my_logger::get(), debug) << "ACK_ID has been assigned: " << ack_id;

    //this->Daq_Addr = n["DAQ_ADDR"].as<string>();
    //cout << "After setting DAQ_ADDR" << endl;

    //this->Visit_ID = n["VISIT_ID"].as<string>();
    //cout << "After setting VISIT_ID" << endl;

    string message_type = "AT_FWDR_XFER_PARAMS_ACK";
    //string component = "AR";
    string ack_bool = "true";

    ostringstream message;
    message << "{ MSG_TYPE: " << message_type
            << ", COMPONENT: " << this->Component
            << ", ACK_ID: " << ack_id
            << ", ACK_BOOL: " << ack_bool << "}";

    FWDR_pub->publish_message(this->Foreman_Reply_Queue, message.str());
    LOGGER(my_logger::get(), debug) << "AT_XFER_PARAMS_ACK is sent to: " << this->Foreman_Reply_Queue; 
    LOGGER(my_logger::get(), debug) << "Message is: " << message.str(); 
    LOGGER(my_logger::get(), info) << "Processing at_transfer params is complete."; 
    return;
}

void Forwarder::process_take_images(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_take_images function."; 
    this->Num_Images = n["NUM_IMAGES"].as<int>();;
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

    //If DAQ == 'API':  pass manifold into new fetch_and_reassemble class
    string image_id = n["IMAGE_ID"].as<string>();
    string msg_type = "FETCH_AT_END_READOUT";
    ostringstream message;
    message << "{MSG_TYPE: " << msg_type
            << ", IMAGE_ID: " << image_id << "}";
    this->FWDR_to_fetch_pub->publish_message(this->fetch_consume_queue, message.str());
    LOGGER(my_logger::get(), debug) << "FETCH_AT_END_READOUT is sent to: " << this->fetch_consume_queue; 
    LOGGER(my_logger::get(), debug) << "Message is: " << message.str(); 
    return;
}

///////////////////////////////////////////////////////////////////
// FETCH THREAD
///////////////////////////////////////////////////////////////////

//From forwarder main thread to fetch thread:
void Forwarder::process_fetch(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_fetch function."; 
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
        LOGGER(my_logger::get(), debug) << "FORMAT_TAKE_IMAGES_DONE is sent to: " << this->format_consume_queue; 
        LOGGER(my_logger::get(), debug) << "Message is: " << msg; 
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
      ostringstream dir_prefix;
      dir_prefix << this->Work_Dir << "/" << image_id;
      LOGGER(my_logger::get(), debug) << "Directory prefix for image segments is: " << dir_prefix; 
      for (int i = 0; i < this->visit_raft_list.size(); i++) {
          for (int j = 0; j < this->visit_ccd_list_by_raft[i].size(); j++) {
              ostringstream cmd;
              ostringstream filepath;
              filepath << dir_prefix.str() << "/" \
                       << this->visit_raft_list[i] << "/" \
                       << this->visit_ccd_list_by_raft[i][j];
              cmd << "mkdir -p " << filepath.str();
              const std::string tmpstr = cmd.str();
              const char* cmdstr = tmpstr.c_str();
              system(cmdstr);
          }
      }
      LOGGER(my_logger::get(), debug) << "Created directories for image segments."; 

      this->fetch_readout_image(image_id, dir_prefix.str());

      return;
    }
}


void Forwarder::process_at_fetch(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_at_fetch function."; 
    string image_id = n["IMAGE_ID"].as<string>();
    string raft = this->visit_raft_list[0];
    string ccd = this->visit_ccd_list_by_raft[0][0];
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
 
    this->fetch_at_reassemble_process(raft, image_id, dir_prefix.str());

    return;
}


void Forwarder::fetch_at_reassemble_process(std::string raft, string image_id, string dir_prefix) {
    LOGGER(my_logger::get(), debug) << "Entering fetch_at_reassemble_process function."; 
    IMS::Store store(raft.c_str()); //DAQ Partitions must be set up to reflect DM name for a raft,
                                    // such as raft01, raft13, etc.

    IMS::Image image(image_id.c_str(), store);

    DAQ::LocationSet sources = image.sources();

    uint64_t total_stripes = 0;

    DAQ::Location location;

    std::ostringstream ccd_path;

    // As spectrograph camera is just one sensor on one partition,
    // the ccd name will be the first ccd string in the list for 
    // the first (and only) raft.
    //
    string ccd = this->visit_ccd_list_by_raft[0][0];

    while(sources.remove(location)) {
        IMS::Source source(location, image);
 
        //should be wfs here 
        IMS::WaveFront slice(source);
        if(!slice) return;
  
        ccd_path << dir_prefix << "/" << raft << "/" << ccd;

        // Filehandle set for ATS CCD will then have a set of 
        // 16 filehandles...one filehandle for each amp segment.
        // 
        std::vector<std::ofstream*> FH_ATS;
        this->fetch_set_up_at_filehandles(FH_ATS, image_id, ccd_path.str());

  
        do {
            total_stripes += slice.stripes();
            IMS::Stripe* ccd0 = new IMS::Stripe [slice.stripes()];
    
            slice.decode(ccd0);
    
            for(int s=0; s<slice.stripes(); ++s) {
                for(int amp=0; amp<N_AMPS; ++amp) {
                    // int32_t X = WFS_PIX_MASK ^ ((ccd0[s].segment[amp]));
                    // Changed at Tucson exercise with actual camera
                    // as this mask worked there...
                    int32_t X = STRAIGHT_PIX_MASK ^ ((ccd0[s].segment[amp]));
                    FH_ATS[amp]->write(reinterpret_cast<const char *>(&X), 4); //32 bits...
                }
            }
    
            delete [] ccd0;
        }
        while(slice.advance());
  
        this->fetch_close_filehandles(FH_ATS);
        string new_msg_type = "FORMAT_END_READOUT";
        ostringstream msg;
        msg << "{MSG_TYPE: " << new_msg_type
            << ", IMAGE_ID: " << image_id
            << ", RAFT: " << raft
            << ", CCD: " << ccd
            << ", PATH: " << ccd_path.str() << "}";
        this->fetch_pub->publish_message(this->format_consume_queue, msg.str());
        LOGGER(my_logger::get(), debug) << "FORMAT_END_READOUT is sent to: " << this->format_consume_queue; 
        LOGGER(my_logger::get(), debug) << "Message is: " << msg; 
    }
    return;
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


void Forwarder::fetch_readout_image(string image_id, string dir_prefix) {
    LOGGER(my_logger::get(), debug) << "Entering fetch_readout_image function."; 
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
    LOGGER(my_logger::get(), debug) << "Entering fetch_readout_raft function."; 
    // put a map together with raft electronic board (source) for key, and ccd_list as value
    map<string, vector<string>> source_boards;
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
  // but the source_boards map generated above may not include keys for all 3 source boards.
  // If ccd list is especially sparse, only one board might be included in map.

  this->fetch_reassemble_raft_image(raft, source_boards, image_id, dir_prefix);

}


void Forwarder::fetch_reassemble_raft_image(string raft, map<string, 
                                            vector<string>> source_boards, 
                                            string image_id, string dir_prefix){
    LOGGER(my_logger::get(), debug) << "Entering fetch_reassemble_raft_image function."; 

  IMS::Store store(raft.c_str()); //DAQ Partitions must be set up to reflect DM name for a raft,
                                  // such as raft01, raft13, etc.

  IMS::Image image(image_id.c_str(), store);

  DAQ::LocationSet sources = image.sources();

  DAQ::Location location;

  int board = 0; // Only way we know how to access a board is by its integer id.


  //The loop below processes each raft board (an individual source) one at a time.
  //In order to avoid boards that do not have desired CCDs on them, we check within
  //this loop; if board is not needed, we skip processing it. This is done by
  //converting the board counter to a string, and checking within the source_boards map
  //for a key representing the current board. If it exists, send board(location) to
  //reassemble process

#ifdef METRIX
  auto start = std::chrono::system_clock::now();
  std::time_t start_time = std::chrono::system_clock::to_time_t(start);
  std::cout << "Started raft fetch at " << std::ctime(&start_time) << endl;
#endif

  while(sources.remove(location))
  {
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

          this->fetch_reassemble_process(raft, image_id, location, image, ccds_for_board, dir_prefix);
       }
       board++;
  }
#ifdef METRIX
  auto end = std::chrono::system_clock::now();
 
  std::chrono::duration<double> elapsed_seconds = end-start;
  std::time_t end_time = std::chrono::system_clock::to_time_t(end);
 
  std::cout << "Finished raft fetch at " << std::ctime(&end_time)
            << "elapsed time: " << elapsed_seconds.count() << "s\n";
#endif
  return;
}

void Forwarder::get_register_metadata(const DAQ::Location& location, const IMS::Image& image)
{
    LOGGER(my_logger::get(), debug) << "Entering get_register_metadata function."; 

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
;

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


// Above, the source boards are iterated through one at a time.
// If the requested raft/ccd(s) can be found within the current board, the needed CCD list
// for the current board is sent to this method along with the board location.
// These two args are used to extract the correct data.
// The other two args (raft and image_id) are used in constructing the output filename
//
// First, determine the number of CCDs in the ccds_for_board vector arg.
// the number of ccds + the name of each CCD in the vector will tell us how to decode the slice.
//////////////////////////////////////////////////////////////////////////////////////////////////

void Forwarder::fetch_reassemble_process(std::string raft, string image_id, const DAQ::Location& location, const IMS::Image& image, std::vector<string> ccds_for_board, string dir_prefix)
{

    LOGGER(my_logger::get(), debug) << "Entering fetch_reassemble_process function."; 
  IMS::Source source(location, image);

  IMS::Science slice(source);

  if(!slice) return;

  // Set up filehandles in Ramdisk work area for this board. There must be a 
  // separate filehandle set for each CCD to be fetched. CCDs to be fetched 
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

  for (int x = 0; x < ccds_for_board.size(); x++) {

        if (string(1, ccds_for_board[x][1]) == "0") {
            do_ccd0 = true;

#ifdef METRIX
  auto start = std::chrono::system_clock::now();
  std::time_t start_time = std::chrono::system_clock::to_time_t(start);
  std::cout << "Start building filehandles for " << ccds_for_board[x] << " at " << std::ctime(&start_time) << endl;
#endif
            this->fetch_set_up_filehandles(FH0, image_id, raft, ccds_for_board[x], dir_prefix);
#ifdef METRIX
  auto end = std::chrono::system_clock::now();
 
  std::chrono::duration<double> elapsed_seconds = end-start;
  std::time_t end_time = std::chrono::system_clock::to_time_t(end);
 
  std::cout << "Finished filehandle creation for " << ccds_for_board[x] << " at " << std::ctime(&end_time)
            << "filehandle creation elapsed time: " << elapsed_seconds.count() << "s\n";
#endif
            ccd0_path << dir_prefix << "/" << raft << "/" << ccds_for_board[x];
            ccd0_map.insert(pair<string,string>("raft",raft));
            ccd0_map.insert(pair<string,string>("ccd",ccds_for_board[x]));
            ccd0_map.insert(pair<string,string>("path",ccd0_path.str()));
        }

        if (string(1, ccds_for_board[x][1]) == "1") {
            do_ccd1 = true;
#ifdef METRIX
  auto start = std::chrono::system_clock::now();
  std::time_t start_time = std::chrono::system_clock::to_time_t(start);
  std::cout << "Start building filehandles for " << ccds_for_board[x] << " at " << std::ctime(&start_time) << endl;
#endif
            this->fetch_set_up_filehandles(FH1, image_id, raft, ccds_for_board[x], dir_prefix);
#ifdef METRIX
  auto end = std::chrono::system_clock::now();
 
  std::chrono::duration<double> elapsed_seconds = end-start;
  std::time_t end_time = std::chrono::system_clock::to_time_t(end);
 
  std::cout << "Finished filehandle creation for " << ccds_for_board[x] << " at " << std::ctime(&end_time)
            << "filehandle creation elapsed time: " << elapsed_seconds.count() << "s\n";
#endif
            ccd1_path << dir_prefix << "/" << raft << "/" << ccds_for_board[x];
            ccd1_map.insert(pair<string,string>("raft",raft));
            ccd1_map.insert(pair<string,string>("ccd",ccds_for_board[x]));
            ccd1_map.insert(pair<string,string>("path",ccd1_path.str()));
        }

        if (string(1, ccds_for_board[x][1]) == "2") {
            do_ccd2 = true;
#ifdef METRIX
  auto start = std::chrono::system_clock::now();
  std::time_t start_time = std::chrono::system_clock::to_time_t(start);
  std::cout << "Start building filehandles for " << ccds_for_board[x] << " at " << std::ctime(&start_time) << endl;
#endif
            this->fetch_set_up_filehandles(FH2, image_id, raft, ccds_for_board[x], dir_prefix);
#ifdef METRIX
  auto end = std::chrono::system_clock::now();
 
  std::chrono::duration<double> elapsed_seconds = end-start;
  std::time_t end_time = std::chrono::system_clock::to_time_t(end);
 
  std::cout << "Finished filehandle creation for " << ccds_for_board[x] << " at " << std::ctime(&end_time)
            << "filehandle creation elapsed time: " << elapsed_seconds.count() << "s\n";
#endif
            ccd2_path << dir_prefix << "/" << raft << "/" << ccds_for_board[x];
            ccd2_map.insert(pair<string,string>("raft",raft));
            ccd2_map.insert(pair<string,string>("ccd",ccds_for_board[x]));
            ccd2_map.insert(pair<string,string>("path",ccd2_path.str()));
        }
    }

  do
  {
    total_stripes += slice.stripes();
    IMS::Stripe* ccd0 = new IMS::Stripe [slice.stripes()];
    IMS::Stripe* ccd1 = new IMS::Stripe [slice.stripes()];
    IMS::Stripe* ccd2 = new IMS::Stripe [slice.stripes()];

    slice.decode012(ccd0, ccd1, ccd2);
    int num1, num2, num3;

    for(int s=0; s<slice.stripes(); ++s)
    {
      for(int amp=0; amp<N_AMPS; ++amp)
      {
        if (do_ccd0) {
            int32_t X = SCIENCE_PIX_MASK ^ ((ccd2[s].segment[amp])); //NOTE: ccd0 and ccd2
                                                                     // must be swapped here
            FH0[amp]->write(reinterpret_cast<const char *>(&X), 4); //32 bits...
        }
      }

      for(int amp=0; amp<N_AMPS; ++amp)
      {
        if (do_ccd1) {
            int32_t X = SCIENCE_PIX_MASK ^ ((ccd1[s].segment[amp]));
            FH1[amp]->write(reinterpret_cast<const char *>(&X), 4); //32 bits...
        }
      }

      for(int amp=0; amp<N_AMPS; ++amp)
      {
        if (do_ccd2) {
            int32_t X = SCIENCE_PIX_MASK ^ ((ccd0[s].segment[amp]));
            FH2[amp]->write(reinterpret_cast<const char *>(&X), 4); //32 bits...
        }
      }

    }
    delete [] ccd0;
    delete [] ccd1;
    delete [] ccd2;

  }
  while(slice.advance());

  if (do_ccd0) {
    this->fetch_close_filehandles(FH0);
    string new_msg_type = "FORMAT_END_READOUT";
    ostringstream msg;
    msg << "{MSG_TYPE: " << new_msg_type
        << ", IMAGE_ID: " << image_id
        << ", RAFT: " << ccd0_map["raft"]
        << ", CCD: " << ccd0_map["ccd"]
        << ", PATH: " << ccd0_map["path"] << "}";
    this->fetch_pub->publish_message(this->format_consume_queue, msg.str());
    LOGGER(my_logger::get(), debug) << "FORMAT_END_READOUT is sent to: " << this->format_consume_queue; 
    LOGGER(my_logger::get(), debug) << "Message is: " << msg; 
  }
  if (do_ccd1) {
    this->fetch_close_filehandles(FH1);
    string new_msg_type = "FORMAT_END_READOUT";
    ostringstream msg;
    msg << "{MSG_TYPE: " << new_msg_type
        << ", IMAGE_ID: " << image_id
        << ", RAFT: " << ccd1_map["raft"]
        << ", CCD: " << ccd1_map["ccd"]
        << ", PATH: " << ccd1_map["path"] << "}";
    this->fetch_pub->publish_message(this->format_consume_queue, msg.str());
    LOGGER(my_logger::get(), debug) << "FORMAT_END_READOUT is sent to: " << this->format_consume_queue; 
    LOGGER(my_logger::get(), debug) << "Message is: " << msg; 
  }
  if (do_ccd2) {
    this->fetch_close_filehandles(FH2);
    string new_msg_type = "FORMAT_END_READOUT";
    ostringstream msg;
    msg << "{MSG_TYPE: " << new_msg_type
        << ", IMAGE_ID: " << image_id
        << ", RAFT: " << ccd2_map["raft"]
        << ", CCD: " << ccd2_map["ccd"]
        << ", PATH: " << ccd2_map["path"] << "}";
    this->fetch_pub->publish_message(this->format_consume_queue, msg.str());
    LOGGER(my_logger::get(), debug) << "FORMAT_END_READOUT is sent to: " << this->format_consume_queue; 
    LOGGER(my_logger::get(), debug) << "Message is: " << msg; 
  }

  return;
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
                          //<< "_segment." << seg;
                          << "_segment." << this->New_Segment_Names[i];

        std::ofstream * fh = new std::ofstream(fns.str(), std::ios::out | \
                                                std::ios::binary );
        fh_set.push_back(fh); 
    }
}

void Forwarder::fetch_set_up_at_filehandles( std::vector<std::ofstream*> &fh_set, 
                                             string image_id, string full_dir_prefix){
    LOGGER(my_logger::get(), debug) << "Entering fetch_set_up_at_filehandles function."; 
    for (int i=0; i < 16; i++) {
        std::ostringstream fns;
        fns << full_dir_prefix << "/" \
                          << image_id \
                          << "--AUXTEL" \
                          << "-ccd.ATS_CCD" \
                          << "_segment." << this->ATS_Segment_Names[i];

        std::ofstream * fh = new std::ofstream(fns.str(), std::ios::out | \
                                                std::ios::binary );
        fh_set.push_back(fh); 
    }
    LOGGER(my_logger::get(), debug) << "Finished setting up file handlers for image segments."; 
}


void Forwarder::fetch_close_filehandles(std::vector<std::ofstream*> &fh_set) {
    LOGGER(my_logger::get(), debug) << "Entering fetch_close_filehandles function.";

    for (int i = 0; i < 16; i++) {
        fh_set[i]->close();
    }
    LOGGER(my_logger::get(), debug) << "Finished closing file handlers for image segments."; 
}




void Forwarder::process_fetch_ack(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_fetch_ack function.";
    return;
}

void Forwarder::process_fetch_health_check(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_fetch_health_check function.";
    return;
}

void Forwarder::process_fetch_health_check_ack(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_fetch_health_check_ack function.";
    return;
}

void Forwarder::process_format(Node n) {
    LOGGER(my_logger::get(), debug) << "Entering process_format function."; 
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
        LOGGER(my_logger::get(), debug) << "Informing AuxDevice with ack message to queue " << reply_queue << " and content is " << message.str();

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
        if (dir_cmd == -1 && errno != 17) { 
            throw L1CannotCreateDirError("In process_header_ready, forwarder cannot create sub_directory in: " + sub_dir); 
        } 
        LOGGER(my_logger::get(), debug) << "Created sub header directory for image id at " << sub_dir.c_str(); 

        // scp -i ~/.ssh/from_efd felipe@141.142.23x.xxx:/tmp/header/IMG_ID.header to /tmp/header/IMG_ID/IMG_ID.header
        ostringstream cp_cmd; 
	// FIX
        cp_cmd << "scp  "
               << path
               << " " 
               << sub_dir
               << "/"; 
	// cp_cmd << "wget -P " << sub_dir << "/ " << path; 
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
        LOGGER(my_logger::get(), debug) << "Sending header_ready message to queue " << this->format_consume_queue << " and content is " << msg.c_str(); 
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
        Node n; 
        n["RAFT"] = node["RAFT"].as<string>();
        n["CCD"] = node["CCD"].as<string>(); 
        this->readout_img_ids[image_id] = n; 
        this->format_look_for_work(image_id); 
        LOGGER(my_logger::get(), debug) << "Looking header file for current ImageID " << image_id; 
        LOGGER(my_logger::get(), debug) << "Looking work for current Readout pixels is complete."; 
    } 
    catch (exception& e) { 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
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
        LOGGER(my_logger::get(), info) << "Looking work for current Header file is complete."; 
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
        string header = n["HEADER"].as<string>(); 
        string raft_name = n["RAFT"].as<string>();  // raft01
        string ccd_name = n["CCD"].as<string>(); // ccd00
        string fits_dir = Work_Dir + "/fits"; 
        const int dir = mkdir(fits_dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR); 
        LOGGER(my_logger::get(), debug) << "Created directory " << fits_dir << " for assembling images."; 

        format_write_img(img_id, raft_name, ccd_name, header);
        LOGGER(my_logger::get(), debug) << "Start formatting ..."; 
    } 
    catch (exception& e) { 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        cerr << e.what() << endl; 
    } 
}


long* Forwarder::format_read_img_segment(const char *file_path) { 
    try { 
        fstream img_file(file_path, fstream::in | fstream::binary); 
        long len = Naxis_2 * Naxis_1; 
        long *buffer = new long[len]; 
        img_file.seekg(0, ios::beg); 
        img_file.read((char *)buffer, len); 
        img_file.close();
        return buffer;
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

unsigned char** Forwarder::format_assemble_pixels(char *buffer) { 
    try { 
        unsigned char **array = new unsigned char*[Naxis_1]; 
        array[0] = (unsigned char *) malloc( Naxis_2 * Naxis_1 * sizeof(unsigned char)); 

        for (int i = 1; i < Naxis_1; i++) { 
            array[i] = array[i-1] + Naxis_2; 
        } 

        for (int j = 0; j < Naxis_1; j++) {
            for (int i = 0; i < Naxis_2; i++) {

                array[j][i]= buffer[i+j]; 
            } 
        }
        return array;
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_write_img(string img_id, string raft_name, string ccd_name, string header) { 
    LOGGER(my_logger::get(), debug) << "Entering format_write_img function."; 
    try { 
        long len = Naxis_1 * Naxis_2;
        int bitpix = LONG_IMG; 
        long naxis = 2;
        long naxes[2] = { Naxis_1, Naxis_2 }; 
        long fpixel = 1; 
        int status = 0; 
        int hdunum = 2;
        int nkeys; 
        char card[FLEN_CARD]; 
        fitsfile *iptr, *optr; 

        // /mnt/ram/IMG_31/raft01/ccd00/*.segment
        string img_path = Work_Dir + "/" + img_id + "/" + raft_name + "/" + ccd_name;
        string header_path = header;

        // IMG_31--raft01--ccd00.fits
	string dest_filename = img_id + "--" + raft_name + "--" + ccd_name + ".fits";
        string destination = Work_Dir + "/fits/" + dest_filename; 
        LOGGER(my_logger::get(), debug) << "Image file path is " << img_path; 
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

        vector<string> file_names = format_list_files(img_path); 
        vector<string>::iterator it; 
        vector<string> exclude_keywords = {"BITPIX", "NAXIS"}; 
        vector<string>::iterator eit; 
        for (it = file_names.begin(); it != file_names.end(); it++) { 
            fitsfile *pix_file_ptr; 
            int *img_buffer = new int[len];
            string img_segment_name = img_path + "/" + *it 
                                      + "[jL" + STRING(Naxis_1) 
                                      + "," + STRING(Naxis_2) + "]"; 

            // get img pixels
            fits_open_file(&pix_file_ptr, img_segment_name.c_str(), READONLY, &status); 
            fits_read_img(pix_file_ptr, TINT, 1, len, NULL, img_buffer, 0, &status); 
            fits_create_img(optr, bitpix, naxis, naxes, &status); 
            fits_write_img(optr, TINT, 1, len, img_buffer, &status);

            // get header 
            fits_movabs_hdu(iptr, hdunum, NULL, &status); 
            fits_get_hdrspace(iptr, &nkeys, NULL, &status); 
            for (int i = 1; i <= nkeys; i++) { 
                fits_read_record(iptr, i, card, &status); 
	        string card_str = string(card); 
                if (card_str.find("BITPIX") == 0) {} 
                else if (card_str.find("NAXIS") == 0) {} 
                else if (card_str.find("PCOUNT") == 0) {} 
                else if (card_str.find("GCOUNT") == 0) {} 
                else if (card_str.find("XTENSION") == 0) {} 
                else { 
		    fits_write_record(optr, card, &status); 
                } 
            }
            hdunum++;

            // clean up 
            fits_close_file(pix_file_ptr, &status); 
            delete[] img_buffer; 
        } 
        fits_close_file(iptr, &status); 
        fits_close_file(optr, &status); 
        LOGGER(my_logger::get(), debug) << "Formatting image segments into fits file is completed."; 

        format_send_completed_msg(img_id, raft_name, ccd_name, destination, dest_filename);
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

//## When Fits file is finished, let forward process know where finished file resides
//## and provide necessary metadata such as file destination.
void Forwarder::format_send_completed_msg(string image_id, string raft_name, \
                                          string ccd_name, string path, string dest_filename) { 
    LOGGER(my_logger::get(), debug) << "Entering format_send_completed_msg function.";
    try { 
        Emitter msg; 
        msg << BeginMap; 
        msg << Key << "MSG_TYPE" << Value << "FORWARD_END_READOUT"; 
        msg << Key << "IMAGE_ID" << Value << image_id; 
        msg << Key << "RAFT" << Value << raft_name; 
        msg << Key << "CCD" << Value << ccd_name; 
	msg << Key << "PATH" << Value << path; 
	msg << Key << "IMAGE_NAME" << Value << dest_filename; 
        //msg << Key << "CHECKSUM" << Value << csum;
        //msg << Key << "RECEIPT" << Null << receipt;
        msg << EndMap; 
        fmt_pub->publish_message(this->forward_consume_queue, msg.c_str()); 
        LOGGER(my_logger::get(), debug) << "Formatting completed. Sending message to consume queue."; 
        LOGGER(my_logger::get(), debug) << "Format complete message is published to " << this->forward_consume_queue; 
        LOGGER(my_logger::get(), debug) << "Published message is " << msg.c_str();
    } 
    catch (exception& e) { 
        LOGGER(my_logger::get(), critical) << e.what() << endl; 
        cerr << e.what() << endl; 
    } 
} 
///////////////////////////////////////////////////////////////////////////

void Forwarder::format_look_for_work(string image_id) { 
    LOGGER(my_logger::get(), debug) << "Entering format_look_for_work function."; 
    try { 
        /** 
        vector<string>::iterator it;
        map<string, string>::iterator mit;  
        map<string, string>::iterator tid; 
        if (this->readout_img_ids.size() != 0 && this->header_info_dict.size() != 0) { 
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
        */ 
        map<string, Node>::iterator binary_it = this->readout_img_ids.find(image_id); 
        map<string, string>::iterator header_it = this->header_info_dict.find(image_id); 
        if (binary_it != this->readout_img_ids.end() && header_it != this->header_info_dict.end()) { 
            Node n; 
            n["IMAGE_ID"] = image_id; 
            n["HEADER"] = this->header_info_dict[image_id]; 
            n["RAFT"] = this->readout_img_ids[image_id]["RAFT"].as<string>(); 
            n["CCD"] = this->readout_img_ids[image_id]["CCD"].as<string>(); 
            format_assemble_img(n); 

            // cleanup the dictionaries
            this->readout_img_ids.erase(binary_it); 
            //this->header_info_dict.erase(header_it); 
        } 
        else { 
            LOGGER(my_logger::get(), debug) << "No img data from DAQ yet. Waiting to process."; 
        } 
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
        // string img_path = this->Work_Dir + "/fits/" + img_id + ".fits"; 
	string img_path = n["PATH"].as<string>();
	string img_name = n["IMAGE_NAME"].as<string>();
        string raft_name = n["RAFT"].as<string>();
        string ccd_name = n["CCD"].as<string>();
        string dest_path = this->Target_Location + "/" + img_name; 
      
        size_t find_at = dest_path.find("@"); 
        ostringstream bbcp_cmd; 

        if (find_at != string::npos) { 
            bbcp_cmd << "scp -i ~/.ssh/from_efd ";
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
	LOGGER(my_logger::get(), debug) << "File is copied from " << img_path << " to " << dest_path; 



        if (bbcp_cmd_status == 256) { 
            throw L1CannotCopyFileError("In forward_process_end_readout, forwarder cannot copy file: " + bbcp_cmd.str()); 
        }

        this->forward_send_result_set(img_name, dest_path, new_csum);
        LOGGER(my_logger::get(), info) << "READOUT COMPLETE.";
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
  
    this->fwd_pub->publish_message(reply_queue, msg.c_str());
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
  
    this->fwd_pub->publish_message(reply_queue, msg.c_str());
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

int main() {
    Forwarder *fwdr = new Forwarder();
    fwdr->run();
    while(1) {
    }
}


