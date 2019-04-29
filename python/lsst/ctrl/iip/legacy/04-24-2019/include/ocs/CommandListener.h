#include "IIPBase.h"
#include "SAL_MTArchiver.h" 
#include "SAL_CatchupArchiver.h"
#include "SAL_PromptProcessing.h" 
#include "SAL_ATArchiver.h"
#include "ccpp_sal_MTArchiver.h" 
#include "ccpp_sal_CatchupArchiver.h"
#include "ccpp_sal_PromptProcessing.h" 
#include "ccpp_sal_ATArchiver.h"
#include "SimplePublisher.h"

extern int next_timed_ack_id; 
/** CommandListener listens to messages from OCS Bridge. It is a child class of a class called
  * OCS_Bridge which handles configuration file openings and setting up publisher to RabbitMq.
  */ 
class CommandListener : public IIPBase { 
    public: 
	struct ocs_thread_args { 
	    SimplePublisher* publisher; 
	    string publish_queue;
	    string consume_queue;  
            SAL_MTArchiver ar; 
            SAL_CatchupArchiver cu; 
            SAL_PromptProcessing pp; 
            SAL_ATArchiver atar;
	}; 

	ocs_thread_args *command_args;
 
	int timed_ack_id;

	CommandListener(); 

	~CommandListener();
	void setup_resolve_publisher(); 
	void setup_archiver_listeners(); 
	void setup_catchuparchiver_listeners(); 
	void setup_promptprocessing_listeners(); 
	void setup_atArchiver_listeners(); 

	static void *run_resolve_publisher(void *); 
	static string get_next_timed_ack_id(string ack_type); 
	static string get_device(string); 

	static void *run_ar_start(void *); 
	static void *run_ar_enable(void *); 
	static void *run_ar_disable(void *); 
	static void *run_ar_standby(void *); 
	static void *run_ar_enterControl(void *); 
	static void *run_ar_exitControl(void *); 
	static void *run_ar_abort(void *); 

	static void *run_cu_start(void *); 
	static void *run_cu_enable(void *); 
	static void *run_cu_disable(void *); 
	static void *run_cu_standby(void *); 
	static void *run_cu_enterControl(void *); 
	static void *run_cu_exitControl(void *); 
	static void *run_cu_abort(void *); 

	static void *run_pp_start(void *); 
	static void *run_pp_enable(void *); 
	static void *run_pp_disable(void *); 
	static void *run_pp_standby(void *); 
	static void *run_pp_enterControl(void *); 
	static void *run_pp_exitControl(void *); 
	static void *run_pp_abort(void *); 

	static void *run_atar_start(void *); 
	static void *run_atar_enable(void *); 
	static void *run_atar_disable(void *); 
	static void *run_atar_standby(void *); 
	static void *run_atar_enterControl(void *); 
	static void *run_atar_exitControl(void *); 
	static void *run_atar_abort(void *); 
	static void *run_atar_resetFromFault(void *); 
};
