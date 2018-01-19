#include <yaml-cpp/yaml.h>
#include "SimplePublisher.h" 
#include "Consumer_impl.h" 

class Formatter {
    public: 
        Consumer* fmt_consumer; 
        SimplePublisher* fmt_publisher; 
        std::string consumer_addr, publisher_addr; 
        std::string work_dir;
        std::string forward_consume_queue;
        std::string format_consume_queue; 

        Formatter(); 
        ~Formatter();
        void setup_publisher(); 
        void setup_consumer(); 
        void run(); 
        void on_message(std::string); 
        char* read_img_segment(const char*);
        unsigned char** assemble_pixels(char *);
        void write_img(std::string, std::string, std::string);
        void assemble_img(YAML::Node);
        void send_completed_msg(std::string);
}; 
