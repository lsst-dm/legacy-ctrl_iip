#include "SAL_dm.h"
#include "ccpp_sal_dm.h"
#include "os.h"
#include "example_main.h"
#include <string.h>
#include "SimplePublisher.h"

class OCS_Bridge { 
    public: 
	string base_broker_addr; 
	string OCS_PUBLISH; 
	string OCS_CONSUME; 
	SimplePublisher ocs_publisher; 

	OCS_Bridge(); 
	~OCS_Bridge(); 
	void setup_publisher(); 
}; 
