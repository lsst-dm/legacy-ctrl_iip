#include <SimpleAmqpClient/SimpleAmqpClient.h>


/** Rabbitmq Publisher for C++ interface */ 
class SimplePublisher { 
    public: 

        /** AmapClient Channel type that is used to send and receive messages from rabbitmq queue */ 
        AmqpClient::Channel::ptr_t channel;  

        /** amqpurl that is used to connect to rabbitmq server */ 
        std::string url; 

        /** boolean value that checks whether rabbitmq connection was successful */ 
        bool isConnected; 

        /** Rabbitmq Publisher that takes amqpurl to set up publishing messages
          * @param amqpurl where rabbitmq server resides in
          * sample url: "amqp://username:passwd@100.100.0.0/%2fvhost"
          */ 
        SimplePublisher(std::string amqpurl); 

        /** connects the publisher to rabbitmq server
          * @return boolean whether the connection was successful
          */ 
        bool connect();

        /** publish messages to the rabbitmq broker  
          * @param queue_name rabbitmq queue to which the messages are being sent
          * @param msg message dictionary to publish to the queue
          * msg must be in the form of "{ MSG_TYPE: HELLO_WORLD }", which looks like python dictionary 
        void publish_message(std::string queue_name, std::string msg); 
};
