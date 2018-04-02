/////////////////////////////////////////////////////////////////
//

#include <sys/stat.h> 
#include <errno.h>
#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <vector> 
#include <algorithm> 
#include <iostream>
#include <sstream>
#include <pthread.h>
#include <fstream>
#include "Consumer_impl.h"
#include "SimplePublisher.h"
#include "fitsio.h"
#include "Forwarder.h"
#include "Exceptions.h"

#define SECONDARY_HDU 2
#define HEIGHT 512
#define WIDTH 2048

using namespace std;
using namespace YAML;

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

Forwarder::Forwarder() {
    try { 
        Node config_file;
        try {
            config_file = LoadFile("../../ForwarderCfg.yaml");
        }
        catch (YAML::BadFile& e) {
            throw L1ConfigIOError("In constructor, forwarder cannot open ForwarderCfg.yaml"); 
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
        }
        catch (YAML::TypedBadConversion<string>& e) {
            throw L1YamlKeyError("In constructor, forwarder cannot acquire required files from config file."); 
        }

        setup_consumers(BASE_BROKER_ADDR);
        setup_publishers(BASE_BROKER_ADDR);
    } 
    catch (L1ConfigIOError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 1; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl;  
        exit(ERROR_CODE);
    } 
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
        exit(ERROR_CODE); 
    } 
    
}

void Forwarder::setup_consumers(string BASE_BROKER_ADDR){
    //Consumers for Primary Forwarder
    try { 
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
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}

void Forwarder::run() {
    try { 
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
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 

}

void *Forwarder::run_thread(void *pargs) {
    try { 
        arg_struct *params = ((arg_struct *) pargs);
        Consumer *consumer = params->consumer;
        Forwarder *forwarder = params->forwarder;
        callback<Forwarder> on_msg = params->funcptr;
        consumer->run<Forwarder>(forwarder, on_msg);
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}


void Forwarder::setup_publishers(string BASE_BROKER_ADDR){
    //Publishers
    try { 
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
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}


//Messages received by Primary Forwarder from Foreman
void Forwarder::on_foreman_message(string body) {
    cout << "In forwarder callback that receives msgs from AR foreman" << endl;
    cout << "-----------Message Body Is:------------" << endl;
    cout << body << endl;
    cout << "----------------------" << endl;
    try  { 
        Node node = Load(body);
        string message_type = node["MSG_TYPE"].as<string>();
        if (!node["MSG_TYPE"]) { 
            throw L1YamlKeyError("In on_foreman_message, forwarder received unknown MSG_TYPE: " + body); 
        } 
        funcptr action = on_foreman_message_actions[message_type];
        (this->*action)(node);
    } 
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}

//Messages received by Primary Forwarder from fetch thread
void Forwarder::on_fetch_message(string body) {
    cout << "ON_FETCH: " << body << endl;
    try { 
        Node node = Load(body);
        string message_type = node["MSG_TYPE"].as<string>();
        if (!node["MSG_TYPE"]) { 
            throw L1YamlKeyError("In on_fetch_message, forwarder received unknown MSG_TYPE: " + body); 
        } 
        funcptr action = on_fetch_message_actions[message_type];
        (this->*action)(node);
    } 
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}

//Messages received by Primary Forwarder from format thread
void Forwarder::on_format_message(string body) {
    cout << "ON_FORMAT: " << body << endl;
    try { 
        Node node = Load(body);
        string message_type = node["MSG_TYPE"].as<string>();
        if (!node["MSG_TYPE"]) { 
            throw L1YamlKeyError("In on_format_message, forwarder received unknown MSG_TYPE: " + body); 
        } 
        funcptr action = on_format_message_actions[message_type];
        (this->*action)(node);
    } 
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}

//Messages received by Primary Forwarder from forwardthread
void Forwarder::on_forward_message(string body) {
    cout << "ON_FORWARD: " << body << endl;
    try { 
        Node node = Load(body);
        string message_type = node["MSG_TYPE"].as<string>();
        if (!node["MSG_TYPE"]) { 
            throw L1YamlKeyError("In on_forward_message, forwarder received unknown MSG_TYPE: " + body); 
        } 
        funcptr action = on_forward_message_actions[message_type];
        (this->*action)(node);
    } 
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}



//Messages received by the fetch, format, and forward threads
void Forwarder::on_forwarder_to_fetch_message(string body) {
    cout << "In fETCHr callback that receives msgs from main forwarder thread" << endl;
    cout << "-----------Message Body Is:------------" << endl;
    cout << body << endl;
    cout << "----------------------" << endl;
    try { 
        Node node = Load(body);
        string message_type = node["MSG_TYPE"].as<string>();
        if (!node["MSG_TYPE"]) { 
            throw L1YamlKeyError("In on_forwarder_to_fetch_message, forwarder received unknown MSG_TYPE: " + body); 
        } 
        funcptr action = on_forwarder_to_fetch_message_actions[message_type];
        (this->*action)(node);
    } 
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}

void Forwarder::on_forwarder_to_format_message(string body) {
    cout << "In format callback that receives msgs from main forwarder thread" << endl;
    cout << "-----------Message Body Is:------------" << endl;
    cout << body << endl;
    cout << "----------------------" << endl;
    try { 
        Node node = Load(body);
        string message_type = node["MSG_TYPE"].as<string>();
        // if (node["MSG_TYPE"]) { 
        if (!node["MSG_TYPE"]) { 
            throw L1YamlKeyError("In on_forwarder_to_format_message, forwarder received unknown MSG_TYPE: " + body); 
        } 
        funcptr action = on_forwarder_to_format_message_actions[message_type];
        (this->*action)(node);
    } 
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}

void Forwarder::on_forwarder_to_forward_message(string body) {
    cout << "In forward callback that receives msgs from main forwarder thread" << endl;
    cout << "-----------Message Body Is:------------" << endl;
    cout << body << endl;
    cout << "----------------------" << endl;
    try { 
        Node node = Load(body);
        string message_type = node["MSG_TYPE"].as<string>();
        if (!node["MSG_TYPE"]) { 
            throw L1YamlKeyError("In on_forwarder_to_forward_message, forwarder received unknown MSG_TYPE: " + body); 
        } 
        funcptr action = on_forwarder_to_forward_message_actions[message_type];
        (this->*action)(node);
    } 
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}

void Forwarder::process_header_ready(Node n) { 
    try { 
        string main_header_dir = this->Work_Dir + "/header"; 
        const int dir = mkdir(main_header_dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR); 
        if (dir == -1 && errno != 17) { 
            throw L1CannotCreateDirError("In process_header_ready, forwarder cannot create directory in: " + main_header_dir); 
        } 

        if (!n["FILENAME"]) { 
            throw L1YamlKeyError("In process_header_ready, forwarder cannot find message params: FILENAME"); 
        } 

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

        // scp felipe@141.142.23x.xxx:/tmp/header/IMG_ID.header to /tmp/header/IMG_ID/IMG_ID.header
        ostringstream cp_cmd; 
        cp_cmd << "scp -i ~/.ssh/from_efd "
               << path
               << " " 
               << sub_dir
               << "/"; 
        int scp_cmd = system(cp_cmd.str().c_str()); 
        if (scp_cmd == 256) { 
            throw L1CannotCopyFileError("In process_header_ready, forwarder cannot copy file: " + cp_cmd.str()); 
        } 

        string img_idx_wheader = path.substr(img_idx + 1);  
        string header_path = sub_dir + "/" + img_idx_wheader;

        Emitter msg; 
        msg << BeginMap; 
        msg << Key << "MSG_TYPE" << Value << "FORMAT_HEADER_READY"; 
        msg << Key << "IMAGE_ID" << Value << img_id; 
        msg << Key << "FILENAME" << Value << header_path; 
        msg << EndMap; 
        FWDR_to_format_pub->publish_message(this->format_consume_queue, msg.c_str()); 
    } 
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (L1CannotCreateDirError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 20; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (L1CannotCopyFileError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 21; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

//Message action handler methods...
void Forwarder::process_new_visit(Node n) {
    cout << "New Visit Message" << endl;
    return;
}

void Forwarder::process_health_check(Node n) {
    try { 
        if (!n["ACK_ID"] || !n["REPLY_QUEUE"]) { 
            throw L1YamlKeyError("In process_health_check, forwarder cannot find key(s) ACK_ID and/or REPLY_QUEUE"); 
        } 
        string ack_id = n["ACK_ID"].as<string>();
        string reply_queue = n["REPLY_QUEUE"].as<string>();
        string message_type = "AR_FWDR_HEALTH_CHECK_ACK";
        //string component = "AR";
        string ack_bool = "True";

        Emitter message; 
        message << BeginMap; 
        message << Key << "MSG_TYPE" << Value << message_type; 
        message << Key << "COMPONENT" << Value << this->Component; 
        message << Key << "ACK_ID" << Value << ack_id; 
        message << Key << "ACK_BOOL" << Value << ack_bool; 
        message << EndMap; 

        FWDR_pub->publish_message(reply_queue, message.c_str());
        cout << "Health Check request Message, ACK sent to: " << reply_queue << endl;
        return;
    } 
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}

void Forwarder::process_xfer_params(Node n) {
    cout << "Entering process_xfer_params method" << endl;
    cout << "Incoming Node n is " << n <<  endl;

    try { 
        Node p = n["XFER_PARAMS"];
        cout << "Sub Node p is " << p <<  endl;

        this->visit_raft_string_list.clear();
        this->visit_raft_string_list = p["RAFT_LIST"].as<vector<string>>();
        cout << "In process_xfer_params, RAFT_LIST has been ASSIGNED to class var" << endl;

        this->visit_ccd_string_lists_by_raft.clear();
        this->visit_ccd_string_lists_by_raft = p["RAFT_CCD_LIST"].as<std::vector<std::vector<string>>>();
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

        Emitter message; 
        message << BeginMap; 
        message << Key << "MSG_TYPE" << Value << message_type; 
        message << Key << "COMPONENT" << Value << this->Component; 
        message << Key << "ACK_ID" << Value << ack_id; 
        message << Key << "ACK_BOOL" << Value << ack_bool; 
        message << EndMap; 
        FWDR_pub->publish_message(reply_queue, message.c_str());
        return;
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}

void Forwarder::process_take_images(Node n) {
    cout << endl << "IN process_take_images" << endl;
    try { 
        this->Num_Images = n["NUM_IMAGES"].as<int>();;
        cout << "Take Image Message...should be some tasty params here" << endl;
        return;
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}

void Forwarder::process_end_readout(Node n) {
    cout << "IN PROCESS_END_READOUT" << endl;
    // Send IMAGE_ID to fetch thread...use message broker queue as work queue
    //If ForwarderCfg.yaml DAQ val == 'API', draw from actual DAQ emulator,
    //else, DAQ val will equal a path where files can be found.

    //If DAQ == 'API':  pass manifold into new fetch_and_reassemble class
    try { 
        string image_id = n["IMAGE_ID"].as<string>();
        image_id_list.push_back(image_id);
        string msg_type = "FETCH_END_READOUT";
        Emitter message; 
        message << BeginMap; 
        message << Key << "MSG_TYPE" << Value << msg_type; 
        message << Key << "IMAGE_ID" << Value << image_id; 
        message << EndMap; 
        this->FWDR_to_fetch_pub->publish_message(this->fetch_consume_queue, message.c_str());
        return;
    } 
    catch (exception& e) { 
        cerr << e.what() << endl;     
    } 
}

//From forwarder main thread to fetch thread
void Forwarder::process_fetch(Node n) {
    cout << endl << "********IN PROCESS_END_READOUT********" << endl;
    //If message_type FETCH_END_READOUT, 
    //  Make dir using image_id as name under work_dir
    //  Fetch data from DAQ or copy from local drive
    //  Send message to Format thread with image_id as msg_type FORMAT_END_READOUT
    //Else if message_type FETCH_TAKE_IMAGES_DONE,
    //  copy msg ack params and send to Format thread as msg_type FORMAT_TAKE_IMAGES_DONE 

    try { 
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
          string image_id = n["IMAGE_ID"].as<string>();
          ostringstream cmd;
          ostringstream filepath;
          filepath << this->Work_Dir << "/" << image_id;
          cmd << "mkdir " << filepath.str();
          const std::string tmpstr = cmd.str();
          const char* cmdstr = tmpstr.c_str();
          system(cmdstr);

          ostringstream acmd;
          acmd << "cp " << Src_Dir <<"/*  " << filepath.str();
          cout << "fetch_end_readout" << acmd.str() << endl;
          const std::string atmpstr = acmd.str();
          const char* acmdstr = atmpstr.c_str();
          system(acmdstr);
     
          string new_msg_type = "FORMAT_END_READOUT";
          ostringstream msg;
          msg << "{MSG_TYPE: " << new_msg_type
                  << ", IMAGE_ID: " << image_id << "}";
          this->fetch_pub->publish_message(this->format_consume_queue, msg.str());
          return;
        }
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}

void Forwarder::process_take_images_done(Node n) {
    try { 
        string new_msg_type = "FETCH_TAKE_IMAGES_DONE";
        string job_num = n["JOB_NUM"].as<string>();
        string ack_id = n["ACK_ID"].as<string>();
        string reply_queue = n["REPLY_QUEUE"].as<string>();
        // 1) Message fetch to pass along this message when work queue is complete
        // 2) Later, forward thread must generate report
        // 3) Send filename_list of files transferred in report
        // 4) Send checksum_list that corressponds to each file in report

        Emitter msg; 
        msg << BeginMap; 
        msg << Key << "MSG_TYPE" << Value << new_msg_type; 
        msg << Key << "JOB_NUM" << Value << job_num; 
        msg << Key << "REPLY_QUEUE" << Value << reply_queue; 
        msg << Key << "ACK_ID" << Value << ack_id; 
        msg << EndMap;  
        this->FWDR_to_fetch_pub->publish_message(this->fetch_consume_queue, msg.c_str());
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
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
    try { 
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
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
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
    try { 
        string image_id = node["IMAGE_ID"].as<string>(); 
        this->readout_img_ids.push_back(image_id); 
        this->format_look_for_work(); 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_get_header(Node node) { 
    cout << "[f] fgh" << endl; 
    try { 
        string image_id = node["IMAGE_ID"].as<string>(); 
        string filename = node["FILENAME"].as<string>(); 
        cout << "[x] " << image_id << ": " << filename << endl;
        this->header_info_dict[image_id] = filename; 
        this->format_look_for_work(); 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_assemble_img(Node n) {
    cout << "[f] fai" << endl; 
    try { 
        string img_id = n["IMAGE_ID"].as<string>(); 
        string header = n["HEADER"].as<string>(); 
        // create dir  /mnt/ram/FITS/IMG_10
        string fits_dir = Work_Dir + "/FITS"; 
        cout << "[x] fits_dir: " << fits_dir << endl; 
        const int dir = mkdir(fits_dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR); 
        format_write_img(img_id, header);
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}


char* Forwarder::format_read_img_segment(const char *file_path) { 
    try { 
        fstream img_file(file_path, fstream::in | fstream::binary); 
        long len = WIDTH * HEIGHT; 
        char *buffer = new char[len]; 
        img_file.seekg(0, ios::beg); 
        img_file.read(buffer, len); 
        img_file.close();
        return buffer;
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

unsigned char** Forwarder::format_assemble_pixels(char *buffer) { 
    try { 
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
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_write_img(string img, string header) { 
    cout << "[x] fwi" << endl;
    try { 
        long len = WIDTH * HEIGHT;
        int bitpix = LONG_IMG; 
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
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

vector<string> Forwarder::format_list_files(string path) { 
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
        return file_names; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_send_completed_msg(string image_id) { 
    cout << "[f] fscm" << endl;
    try { 
        Emitter msg; 
        msg << BeginMap; 
        msg << Key << "MSG_TYPE" << Value << "FORWARD_END_READOUT"; 
        msg << Key << "IMAGE_ID" << Value << image_id; 
        msg << EndMap; 
        fmt_pub->publish_message(this->forward_consume_queue, msg.c_str()); 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 
///////////////////////////////////////////////////////////////////////////

void Forwarder::format_look_for_work() { 
    cout << "[f] flfw" << endl;
    try { 
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
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

///////////////////////////////////////////////////////////////////////////////
// Forward part 
///////////////////////////////////////////////////////////////////////////////

void Forwarder::forward_process_end_readout(Node n) { 
    try { 
        string img_id = n["IMAGE_ID"].as<string>(); 
        string img_path = this->Work_Dir + "/FITS/" + img_id + ".fits"; 
        string dest_path = this->Target_Location + "/" + img_id + ".fits"; 
      
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
        int bbcp_cmd_status = system(bbcp_cmd.str().c_str()); 
        if (bbcp_cmd_status == 256) { 
            throw L1CannotCopyFileError("In forward_process_end_readout, forwarder cannot copy file: " + bbcp_cmd.str()); 
        } 
        this->finished_image_work_list.push_back(img_id);
        cout << "[X] READOUT COMPLETE." << endl;
    } 
    catch (L1CannotCopyFileError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 21; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::forward_process_take_images_done(Node n) { 
    try { 
        cout << "get here" << endl;
        if (!n["ACK_ID"] || !n["REPLY_QUEUE"]) { 
            throw L1YamlKeyError("In forward_process_take_images_done, forwarder cannot find required params.");
        } 
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
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

int main() {
    Forwarder *fwdr = new Forwarder();
    fwdr->run();
    while(1) {
    }
}
