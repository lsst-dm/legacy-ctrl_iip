#include <iostream> 
#include <exception> 
#include <unistd.h>
#include <stdlib.h>
#include "Consumer.h"

using namespace std; 
using namespace AmqpClient;
  
Consumer::Consumer(string amqp_url, string queue) { 
    URL = amqp_url; 
    EXCHANGE = "message"; 
    QUEUE = queue; 
    SLEEPING_MS = 5000;
    isReconnected = false;
} 

void Consumer::connect() { 
    try { 
        channel = Channel::CreateFromUri(URL); 
        on_connection_open(); 
    } 
    catch (exception& e) { 
        if (!isReconnected)  { 
            cout << "EXCEPTION: " << e.what() << endl; 
            on_connection_closed(); 
        }
        else { exit(EXIT_FAILURE); }   
    } 
} 

void Consumer::on_connection_open() { 
    cout << "Connection was successful" << endl; 
    // setup_exchange(); 
} 

void Consumer::on_connection_closed() { 
    cout << "Connection was closed. " << endl; 
    usleep(SLEEPING_MS);     
    reconnect(); 
} 

void Consumer::reconnect() { 
    isReconnected = true; 
    connect(); 
} 

void Consumer::setup_exchange() { 
    cout << "Setting up exchange" << endl; 
    channel->DeclareExchange(EXCHANGE);
    on_exchange_declareok();
} 

void Consumer::on_exchange_declareok() { 
    cout << "Exchange set up was successful" << endl; 
    setup_queue(); 
} 

void Consumer::setup_queue() { 
    cout << "Setting up queue" << endl; 
    channel->DeclareQueue(QUEUE, false, false, false, false); 
    on_queue_declareok();
} 

void Consumer::on_queue_declareok() { 
    cout << "Queue declare was successful" << endl; 
    on_bind_declareok(); 
} 

void Consumer::on_bind_declareok() { 
    cout << "Binding queue with exchange" << endl; 
    channel->BindQueue(QUEUE, EXCHANGE, QUEUE); 
} 

void Consumer::start_consuming(callback on_message) { 
    cout << "##### Start consuming messages ######" << endl;
    string consume_tag = channel->BasicConsume(QUEUE); 
    while (1) {
        Envelope::ptr_t envelope = channel->BasicConsumeMessage(consume_tag); 
        BasicMessage::ptr_t messageEnv = envelope->Message(); 
        string message = messageEnv->Body();
        on_message(message); 
    }
} 

void Consumer::run(callback on_message) { 
    connect(); 
    start_consuming(on_message); 
} 
