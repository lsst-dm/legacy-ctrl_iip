#include "Consumer.h"
#include <boost/variant.hpp> 
#include "SAL_archiver.h" 
#include "SAL_catchuparchiver.h" 
#include "SAL_processingcluster.h" 

/** Rabbitmq subscriber class to ack back messages from OCS after processing */ 
class AckSubscriber : public OCS_Bridge { 
    public: 
	typedef boost::variant<SAL_archiver, SAL_catchuparchiver, SAL_processingcluster> sal_obj; 
        
        /** Consumer object to listen to messages from rabbitmq */ 
        Consumer* ack_consumer; 

        /** constructor for Rabbitmq ack subscriber to OCS system */ 
	AckSubscriber(); 

        /** destructor of AckSubscriber object */ 
	~AckSubscriber(); 

        /** Set up rabbitmq consumer object */ 
	void setup_consumer(); 

        /** Run rabbitmq IOLoop to listen to messages */ 
	void run(); 

        /** Rabbitmq callback function to parse into Consumer object to listen to messages
          * @param string message body
          */ 
        static void on_message(std::string); 

	static std::string get_salProcessor(std::string, std::string); 

	static sal_obj get_SALObj(std::string); 
}; 

