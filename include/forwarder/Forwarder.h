#include <yaml-cpp/yaml.h>
#include "daq/Location.hh"
#include "daq/LocationSet.hh"

#include "ims/Store.hh"
#include "ims/Image.hh"
#include "ims/Source.hh"
#include "ims/Slice.hh"
#include "ims/Science.hh"

class Forwarder {
    public:

    //Important 'per readout' values
    std::vector<string> visit_raft_string_list;
    std::vector<std::vector<string>> visit_ccd_string_lists_by_raft;
    std::vector<string> image_id_list;

    // ---------------------TODO-----------------------------
    std::vector<string> visit_raft_list; //ask Jim
    std::vector<std::vector<string>> visit_ccd_list_by_raft;
    // std::vector<string> image_id_list;
    // ---------------------------------------------------

    std::vector<string> current_image_work_list;
    std::vector<string> finished_image_work_list;
    std::vector<string> files_transferred_list;
    std::vector<string> checksum_list;

    std::string Session_ID = "";
    std::string Visit_ID = "";
    std::string Job_Num = "";
    // std::string Target_Location = "";
    std::string Target_Location = "/tmp/target"; // TODO
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

    int ERROR_CODE_PREFIX; 

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
    void process_new_visit(YAML::Node n);
    void process_health_check(YAML::Node n);
    void process_xfer_params(YAML::Node n);
    void process_take_images(YAML::Node n);
    void process_take_images_done(YAML::Node n);
    void process_end_readout(YAML::Node n);
    void process_header_ready(YAML::Node n); 

    void process_fetch(YAML::Node n);
    void process_fetch_ack(YAML::Node n);
    void process_fetch_end_readout(YAML::Node n);
    void process_fetch_health_check(YAML::Node n);
    void process_fetch_health_check_ack(YAML::Node n);
    void process_format(YAML::Node n);
    void process_format_ack(YAML::Node n);
    void process_format_health_check(YAML::Node n);
    void process_format_health_check_ack(YAML::Node n);
    void process_forward(YAML::Node n);
    void process_forward_ack(YAML::Node n);
    void process_forward_health_check(YAML::Node n);
    void process_forward_health_check_ack(YAML::Node n);

    void run();
    static void *run_thread(void *);

    void fetch_readout_image(string image_id, string dir_prefix);
    void fetch_readout_raft(string raft, vector<string> ccd_list, string image_id, string dir_prefix);
    void fetch_reassemble_raft_image(string raft, map<string, vector<string>> source_boards, string image_id, string dir_prefix);
    void fetch_reassemble_process(string raft, string image_id, const DAQ::Location& location, const IMS::Image& image, std::vector<string> ccds_for_board, string dir_prefix);
    void fetch_set_up_filehandles(std::vector<std::ofstream*> &fh_set, string image_id, string raft, string ccd, string dir_prefix);
    void fetch_close_filehandles(std::vector<std::ofstream*> &fh_set);

    char* format_read_img_segment(const char*);
    unsigned char** format_assemble_pixels(char *);
    void format_write_img(std::string, std::string);
    void format_assemble_img(YAML::Node);
    void format_send_completed_msg(std::string);
    void format_look_for_work(); 
    void format_process_end_readout(YAML::Node); 
    void format_get_header(YAML::Node); 
    vector<string> format_list_files(string); 

    void forward_process_end_readout(YAML::Node); 
    void forward_process_take_images_done(YAML::Node); 
};
