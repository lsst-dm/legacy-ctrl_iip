#include "SAL_archiver.h" 
#include "SAL_catchuparchiver.h" 
#include "SAL_processingcluster.h" 


extern int next_timed_ack_id; 
/** CommandListener listens to messages from OCS Bridge. It is a child class of a class called
  * OCS_Bridge which handles configuration file openings and setting up publisher to RabbitMq.
  */ 
class CommandListener : public OCS_Bridge { 
    public: 
	struct ocs_thread_args { 
	    SimplePublisher* publisher; 
	    string publish_queue;
	    string consume_queue;  
	}; 

	ocs_thread_args *command_args;
 
	int timed_ack_id;

	CommandListener(); 

	~CommandListener();
	void setup_resolve_publisher(); 
	void setup_archiver_listeners(); 
	void setup_catchuparchiver_listeners(); 
	void setup_processingcluster_listeners(); 

	static void *run_resolve_publisher(void *); 
	static string get_next_timed_ack_id(string ack_type); 
	static string get_device(string); 

	static void *run_ar_start(void *); 
	static void *run_ar_stop(void *); 
	static void *run_ar_enable(void *); 
	static void *run_ar_disable(void *); 
	static void *run_ar_standby(void *); 
	static void *run_ar_enterControl(void *); 
	static void *run_ar_exitControl(void *); 
	static void *run_ar_abort(void *); 

	static void *run_cu_start(void *); 
	static void *run_cu_stop(void *); 
	static void *run_cu_enable(void *); 
	static void *run_cu_disable(void *); 
	static void *run_cu_standby(void *); 
	static void *run_cu_enterControl(void *); 
	static void *run_cu_exitControl(void *); 
	static void *run_cu_abort(void *); 

	static void *run_pp_start(void *); 
	static void *run_pp_stop(void *); 
	static void *run_pp_enable(void *); 
	static void *run_pp_disable(void *); 
	static void *run_pp_standby(void *); 
	static void *run_pp_enterControl(void *); 
	static void *run_pp_exitControl(void *); 
	static void *run_pp_abort(void *); 
};
