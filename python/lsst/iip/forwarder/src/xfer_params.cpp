#include <yaml-cpp/yaml.h> 
#include <iostream> 
#include "SimplePublisher.h" 
#include "Consumer_impl.h" 

using namespace std; 
using namespace YAML; 

class A { 
    public:
    void on_message(string); 
    void mrun(); 
}; 

void A::on_message(string msg) { 
    cout << "Message from ARCHIE is " << endl; 
    cout << msg << endl;
    cout << "-------------" << endl;
    Node n = Load(msg); 
    
    // START
    vector<string> llist; 
    Node t = n["MMAP"]; 
    string key = t["KEY"].as<string>(); 
    vector<vector<string>> list = t["LIST"].as<vector<vector<string> > >(); 

    vector<vector<string> >::iterator outer; 
    vector<string>::iterator inner; 

    for (outer = list.begin(); outer != list.end(); outer++) { 
        for (inner = outer->begin(); inner != outer->end(); inner++) { 
            cout << *inner << " "; 
        } 
        cout << endl; 
    } 
    cout << "DONE" << endl;
    cout << endl;

} 

void A::mrun() { 
    Consumer *c = new Consumer("amqp://PFM:PFM@141.142.238.10/%2ftest", "f9_consume_from_format"); 
    callback<A> on_msg = &A::on_message; 
    c->run<A>(this, on_msg); 
} 

int main() { 
    /** 
    Node n = Load("{hello: world, my: [1, 2]}"); 
     
    vector<string> hello; 
    hello = n["my"].as<vector<string>>(); 

    vector<string>::iterator it; 
    for (it = hello.begin(); it != hello.end(); it++) { 
        cout << *it << " " ; 
    } 
    cout << endl; 
    cout << n << endl;

    Node r = Load("{ m: [[1, 2], [2, 3]], j: my }"); 
    vector<vector<string> > m; 
    m = r["m"].as<vector<vector<string> > >(); 

    vector<vector<string> >::iterator outer; 
    vector<string>::iterator inner; 

    for (outer = m.begin(); outer != m.end(); outer++) { 
        for (inner = outer->begin(); inner != outer->end(); inner++) { 
            cout << *inner << " "; 
        } 
        cout << endl; 
    } 
    cout << "DONE" << endl;
    cout << endl;
    */ 
    A *a; 
    a->mrun();
    return 0;
} 
