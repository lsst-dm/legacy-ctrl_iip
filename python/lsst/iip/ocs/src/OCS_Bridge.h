#include "SAL_dm.h"
#include "ccpp_sal_dm.h"
#include "os.h"
#include "example_main.h"
#include <string.h>
#include <SimpleAmqpClient/SimpleAmqpClient.h>

class OCS_Bridge { 
    public: 
	string base_broker_addr; 
	string OCS_PUBLISH; 
	string OCS_CONSUME; 
	AmqpClient::Channel::ptr_t ocs_publisher; 

	OCS_Bridge(); 
	~OCS_Bridge(); 
	static void process_ocs_message(AmqpClient::Channel::ptr_t, string, string); 
	void setup_publisher(); 
}; 
