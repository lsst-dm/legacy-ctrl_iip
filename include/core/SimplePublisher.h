#include <SimpleAmqpClient/SimpleAmqpClient.h>

class SimplePublisher { 
    public: 
        SimplePublisher(std::string); 
        void publish_message(std::string, std::string); 

    private:
        AmqpClient::Channel::ptr_t _channel;  
};
