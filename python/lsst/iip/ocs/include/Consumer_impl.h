#include "Consumer.h" 
#include <iostream> 

using namespace std; 
using namespace AmqpClient;

template <typename T>
void Consumer::run(T *t, callback<T> on_message) { 
    cout << "##### Start consuming messages ######" << endl;
    connect(); 
    string consume_tag = channel->BasicConsume(QUEUE); 
    while (1) {
        Envelope::ptr_t envelope = channel->BasicConsumeMessage(consume_tag); 
        BasicMessage::ptr_t messageEnv = envelope->Message(); 
        string message = messageEnv->Body();
        (t->*on_message)(message); 
    }
} 
