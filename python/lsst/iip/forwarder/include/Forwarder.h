////////////////////////////////////////////////////////////////
//
#include <sys/stat.h> 
#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <vector> 
#include <algorithm> 
#include <iostream>
#include <ios>
#include <sstream>
#include <pthread.h>
#include <fstream>
#include <chrono>
#include <ctime>
#include <cstdlib>
#include <yaml-cpp/yaml.h>
#include "Consumer_impl.h"
#include "SimplePublisher.h"
#include "fitsio.h"
#include <errno.h>
#include "Exceptions.h"

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

using namespace std;
using namespace YAML;

class Forwarder {
    public:

    //Important 'per readout' values
    std::vector<string> visit_raft_list;
    std::vector<std::vector<string>> visit_ccd_list_by_raft;

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
    bool is_naxis_set = true;
    long Naxis_1 = NAXIS1;
    long Naxis_2 = NAXIS2;
    int Num_Images = 0; 
    int ERROR_CODE_PREFIX; 
    //std::vector<string> Segment_Names = {"00","01","02","03","04","05","06","07",\
    //                                     "10","11","12","13","14","15","16","17"};
   
    //std::vector<string> New_Segment_Names = {"10","11","12","13","14","15","16","17",\
    //                                         "00","01","02","03","04","05","06","07"};

    // Works for main cam
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
    
    string USER, PASSWD, BASE_BROKER_ADDR, FQN, HOSTNAME, IP_ADDR;
    string CONSUME_QUEUE, USER_FORWARD_PUB, PASSWD_FORWARD_PUB;
    string USER_PUB, PASSWD_PUB, USER_FETCH_PUB, PASSWD_FETCH_PUB, USER_FORMAT_PUB, PASSWD_FORMAT_PUB;
    string FETCH_USER, FETCH_USER_PASSWD, FORMAT_USER, FORMAT_USER_PASSWD,  FORWARD_USER, FORWARD_USER_PASSWD;
    string FETCH_USER_PUB, FETCH_USER_PUB_PASSWD, FORMAT_USER_PUB, FORMAT_USER_PUB_PASSWD; 
    string FORWARD_USER_PUB, FORWARD_USER_PUB_PASSWD;

    map<string, Node> readout_img_ids; 
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

    void fetch_readout_image(string image_id, string dir_prefix);
    void fetch_readout_raft(string raft, vector<string> ccd_list, string image_id, string dir_prefix);
    void fetch_reassemble_raft_image(string raft, map<string, vector<string>> source_boards, string image_id, string dir_prefix);
    void fetch_reassemble_process(string raft, string image_id, const DAQ::Location& location, const IMS::Image& image, std::vector<string> ccds_for_board, string dir_prefix);
    void fetch_at_reassemble_process(string raft, string image_id, string dir_prefix);
    void get_register_metadata(const DAQ::Location& location, const IMS::Image& image);
    void fetch_set_up_filehandles(std::vector<std::ofstream*> &fh_set, string image_id, string raft, string ccd, string dir_prefix);
    void fetch_set_up_at_filehandles(std::vector<std::ofstream*> &fh_set, string image_id, string dir_prefix);
    void fetch_close_filehandles(std::vector<std::ofstream*> &fh_set);

    long* format_read_img_segment(const char*);
    unsigned char** format_assemble_pixels(char *);
    void format_write_img(std::string, std::string, std::string, std::string);
    void format_assemble_img(Node);
    void format_send_completed_msg(std::string, std::string, std::string, std::string,std::string);
    void format_look_for_work(std::string); 
    void format_process_end_readout(Node); 
    void format_get_header(Node); 
    vector<string> format_list_files(string); 

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
    { "01", 0},
    { "02", 0},
    { "10", 1},
    { "11", 1},
    { "12", 1},
    { "20", 2},
    { "21", 2},
    { "22", 2}

};

map<string, vector<string>> All_Boards = {
    { "0", {"00","01","02"}},
    { "1", {"10","11","12"}},
    { "2", {"20","21","22"}}

};

