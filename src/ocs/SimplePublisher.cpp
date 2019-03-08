#include <iostream>
#include <exception>
#include <stdio.h>
#include "SimplePublisher.h"

using namespace std; 
using namespace AmqpClient; 

SimplePublisher::SimplePublisher(string amqpurl) { 
    url = amqpurl;
    isConnected = connect(); 
}

bool SimplePublisher::connect() { 
    bool connection; 
    try { 
        channel = Channel::CreateFromUri(url); 
        connection = true; 
    } 
    catch (exception& e) { 
        connection = false; 
        cout << "Connection was not succesful." << endl; 
        cout << "SimplePublisher is quitting ... " << endl; 
        exit(100); 
    } 
    return connection;
}

void SimplePublisher::publish_message(string queue_name, string msg) {
    if (isConnected) { 
        BasicMessage::ptr_t message = BasicMessage::Create(msg); 
        channel->BasicPublish("", queue_name, message); 
    } 
}
