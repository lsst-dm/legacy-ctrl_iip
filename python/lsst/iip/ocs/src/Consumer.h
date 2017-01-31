#include <SimpleAmqpClient/SimpleAmqpClient.h>

/** callback function to implement in the client class to retrieve messages
  * @param body message body that is passed from rabbitmq queue
  */ 
typedef void (*callback)(std::string body); 

/** Rabbitmq message consumer for C++ interface, used to listen to messages from the queue
  * Consumer object uses AmqpClient Channel object, which is intended for one channel per object.
  * If we need more consumer/listener for message queue, each consumer should create its channel. 
  */ 
class Consumer { 
    public:

        /** amqpurl where rabbitmq server resides in */  
        std::string URL; 

        /** AmqpClient Channel object that is used to send/receive messages from broker */ 
        AmqpClient::Channel::ptr_t channel; 

        /** Rabbitmq Exchange name, default is "message" */ 
        std::string EXCHANGE; 

        /** Rabbitmq Queue to which messages are delivered */ 
        std::string QUEUE; 

        /** sleep delay to wait before reconnecting to broker if connection was unsuccessful */  
        unsigned int SLEEPING_MS;

        /** boolean value to check whether the connection to broker was successful */ 
        bool isReconnected;

        /** Rabbitmq message listener object, interface for C++
          * @param amqpurl url to connect to rabbitmq broker 
          * @param queue listen to messages from this particular queue
          */ 
        Consumer(std::string amqpurl, std::string queue); 

        /** connect to rabbitmq broker
          * if connection was successful, calls on_connection_open() method 
          * if connection was not successful, calls on_connection_closed() method 
          */ 
        void connect();

        /** since connection to broker was successful, calling setting up message exchange */  
        void on_connection_open(); 

        /** connection to broker was unsuccessful and setting up for reconnection. */ 
        void on_connection_closed();    

        /** reconnect to message broker 
          * if reconnection fails, calls sys.exit and quit the program
          */ 
        void reconnect(); 
        
        /** setting up rabbitmq exchange to listen to messages from 
          * default exchange is "message" 
          */ 
        void setup_exchange(); 

        /** exchange declaration was okay and call setting up queue */ 
        void on_exchange_declareok(); 

        /** setting up queue to listen to messages
          * if queue isn't declared in advanced, this is the method that will be called
          * automatically to declare queue
          */ 
        void setup_queue(); 

        /** queue declaration was successful and moving onto queue_binding */ 
        void on_queue_declareok(); 

        /** run is the entry into consumer class from client
          * run implements connection to the broker and message listening
          * @param callback function to pass as a listener for message
          */ 
        void run(callback); 
        
        /** bind queue with exchange */ 
        void on_bind_declareok();
        
        /** start_consuming is the ioloop that checks the queue 
          * as soon as messages are queued, start_consuming unpacks its BasicMessage into string of message body
          * and passes the return value to the callback function 
          */ 
        void start_consuming(callback); 
}; 
