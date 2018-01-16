#include <iostream> 
#include <pthread.h>
#include <yaml-cpp/yaml.h>
#include <vector>
#include <stdio.h>
#include "Consumer_impl.h" 

using namespace std; 
using namespace YAML; 

// header part 
class Subscriber { 
    public: 
    Consumer *consumer; 
    std::vector<string> visit_raft_list;

    Subscriber(); 
    ~Subscriber(); 
    void setup_consumer(); 
    void on_message(string body); 
    void do_something(Node n); 
    void run();
    static void *run_thread(void *);
}; 

// implementation starts here
using funcptr = void (Subscriber::*)(Node); 

struct arg_struct { 
    Consumer *consumer;
    Subscriber *subscriber; 
};

map<string, funcptr> action_handler = { 
    { "DO_SOMETHING", &Subscriber::do_something}, 
}; 

Subscriber::Subscriber() {
    setup_consumer();
} 

Subscriber::~Subscriber() {} 

void Subscriber::setup_consumer() { 
    consumer = new Consumer("amqp://AFM:AFM@141.142.238.10/%2fbunny", "ocs_dmcs_consume"); 
} 

void Subscriber::on_message(string body) { 
    Node node = Load(body); 
    string message_type = node["MSG_TYPE"].as<string>(); 
    funcptr action = action_handler[message_type]; 
    (this->*action)(node); 
} 

// IMPLEMENT ME 
void Subscriber::do_something(Node n) { 
    //string device = n["DEVICE"].as<string>(); 
    //
    //METHOD #1
    //std::vector<string> raft_list = n["RAFT_LIST"].as<string>(); 
    //for(string s : raft_list) {
    //     std::cout << s << '\n';
    //
    //METHOD #2
    //for(vector<string>::const_iterator i = raft_list.begin(); i != raft_list.end(); ++i) {
    //    cout << i << "\n";
    //}
    //
    //METHOD #3
    std::vector<string> rafts;
    std::vector<string> raft_ccds;
    unsigned short num_rafts = n["RAFT_LIST"].size();
    for (unsigned short f = 0; f < num_rafts; f++) {
        rafts.push_back(n["RAFT_LIST"][f].as<string>()); 
        //raft_ccds.push_back(n["RAFT_CCD_LIST"][f].as<string>()); 
    //    rafts.push_back(n["RAFT_LIST"][f].as(basic_string<char>)()); 
    //    cout << "RAFT_LIST member: " << n["RAFT_LIST"][f] << endl; 
        cout << "RAFT_LIST member from vector: " << rafts[f] << endl; 
        //cout << "RAFT_CCD_LIST member from vector of vectors: " << rafts[f] << endl; 
    }
    this->visit_raft_list = rafts;
    cout << "Class Var vector visit_raft_list[2] is: " << visit_raft_list[2] << endl; 
    //
    //METHOD #4
    //std::string rafter = n["RAFT_LIST"].as<std::string>(); 
    //printf("Raft list is %s", n["RAFT_LIST"]);
    //std::list<string> rafter = n["RAFT_LIST"].as<std::list<string>>(); 
    //cout << "RAFT_LIST param looks like this: " << rafter << endl;
    //std::vector<basic_string<char>> rafts;
    //unsigned short num_rafts = n["RAFT_LIST"].size();
    //for (unsigned short f = 0; f < num_rafts; f++) {
    //    rafts.push_back(n["RAFT_LIST"][f].as<basic_string<char>>()); 
    //    cout << "RAFT_LIST member: " << rafts[f] << endl; 
    //}
    //
    //METHOD #5
    //unsigned short num_rafts = n["RAFT_LIST"].size();
    //string rafts[num_rafts];
    //for (unsigned short f = 0; f < num_rafts; f++) {
    //    rafts.push_back(n["RAFT_LIST"][f].as<string>()); 
    //    rafts[f] = n["RAFT_LIST"][f]; 
    //    cout << "RAFT_LIST member: " << rafts[f] << endl; 
    //}
    //
    //cout << "[x] I did something and device is " << device << endl; 
} 
//std::vector<std::basic_string<char> >
void Subscriber::run() { 
    cout << "Consumer running ..." << endl;

    arg_struct *args = new arg_struct; 
    args->consumer = consumer; 
    args->subscriber = this; 

    pthread_t t;
    pthread_create(&t, NULL, &Subscriber::run_thread, args); 
} 

void *Subscriber::run_thread(void *pargs) {
    arg_struct *params = ((arg_struct *) pargs); 
    Consumer *consumer = params->consumer;
    Subscriber *subscriber = params->subscriber;

    callback<Subscriber> on_msg = &Subscriber::on_message;
    consumer->run<Subscriber>(subscriber, on_msg); 
} 

int main() { 
    Subscriber *sub = new Subscriber(); 
    sub->run(); 
    
    pthread_exit(NULL); 
    return 0;
} 
