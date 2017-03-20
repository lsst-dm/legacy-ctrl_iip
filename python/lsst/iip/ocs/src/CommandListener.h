#include "SAL_archiver.h" 
#include "SAL_catchuparchiver.h" 
#include "SAL_processingcluster.h" 


extern int next_timed_ack_id; 
/** CommandListener listens to messages from OCS Bridge. It is a child class of a class called
  * OCS_Bridge which handles configuration file openings and setting up publisher to RabbitMq.
  */ 
class CommandListener : public OCS_Bridge { 
    public: 
        /** ocs thread arguments to pass to the pthread
          * @dmgr SAL dm manager to listen to messages from DDS
          * @publisher SimplePublisher object to send messages to DMCS
          * @q queue name to send messages to DMCS
          */ 
	struct ocs_thread_args { 
	    SAL_archiver archie; 
	    SAL_catchuparchiver catchuparchie; 
	    SAL_processingcluster processie; 
	    SimplePublisher* publisher; 
	    string queue; 
	}; 

        /** ocs command arguements to pass to pthread */ 
	ocs_thread_args *command_args;
 
        /** SAL dm manager to listen to messages from DDS */ 
	SAL_archiver archiver; 
	SAL_catchuparchiver catchuparchiver; 
	SAL_processingcluster processingcluster;

        /** pthread to listen to messages in the background */ 
	pthread_t ocsthread; 

	// ack_id 
	int timed_ack_id;

        /** constructor for CommandListener */ 
	CommandListener(); 

        /* destructor for CommandListener */
	~CommandListener();

        /* set up a consumer for OCS commands */
	void setup_ocs_consumer(); 

        /** run OCS consumer to consume messages
          * OCS sends commands via devices called start_commander, stop_commander, ...
          * This method uses accepting devices called start_controller, stop_controller, ... to receive messages
          * from OCS.
          * @param *pargs arguments passed to the thread
          */ 
	static void *run_ocs_consumer(void *); 

        /** dm_start is used in run_ocs_consumer to accept messages from OCS system via device called start_commander
          * @param cmdId command id issued by the SAL
          * @param timeout timeout to use with the controller
          * @param delay_10ms delay milliseconds
          * @param publisher publisher object to send messages to Rabbitmq 
          * @param queue queue name to send messages to 
          * @param mgr SAL_dm manager to handle acceptance of messages from OCS
          */ 
	static void archiver_start(int, int, os_time, SimplePublisher*, string, SAL_archiver);
	static void archiver_stop(int, int, os_time, SimplePublisher*, string, SAL_archiver);
	static void archiver_enable(int, int, os_time, SimplePublisher*, string, SAL_archiver);
	static void archiver_disable(int, int, os_time, SimplePublisher*, string, SAL_archiver);
	static void archiver_standby(int, int, os_time, SimplePublisher*, string, SAL_archiver);
	static void archiver_abort(int, int, os_time, SimplePublisher*, string, SAL_archiver);
	static void archiver_enterControl(int, int, os_time, SimplePublisher*, string, SAL_archiver);
	static void archiver_exitControl(int, int, os_time, SimplePublisher*, string, SAL_archiver);


	static void catchuparchiver_start(int, int, os_time, SimplePublisher*, string, SAL_catchuparchiver);
	static void catchuparchiver_stop(int, int, os_time, SimplePublisher*, string, SAL_catchuparchiver);
	static void catchuparchiver_enable(int, int, os_time, SimplePublisher*, string, SAL_catchuparchiver);
	static void catchuparchiver_disable(int, int, os_time, SimplePublisher*, string, SAL_catchuparchiver);
	static void catchuparchiver_standby(int, int, os_time, SimplePublisher*, string, SAL_catchuparchiver);
	static void catchuparchiver_abort(int, int, os_time, SimplePublisher*, string, SAL_catchuparchiver);
	static void catchuparchiver_enterControl(int, int, os_time, SimplePublisher*, string, SAL_catchuparchiver);
	static void catchuparchiver_exitControl(int, int, os_time, SimplePublisher*, string, SAL_catchuparchiver);


	static void processingcluster_start(int, int, os_time, SimplePublisher*, string, SAL_processingcluster);
	static void processingcluster_stop(int, int, os_time, SimplePublisher*, string, SAL_processingcluster);
	static void processingcluster_enable(int, int, os_time, SimplePublisher*, string, SAL_processingcluster);
	static void processingcluster_disable(int, int, os_time, SimplePublisher*, string, SAL_processingcluster);
	static void processingcluster_standby(int, int, os_time, SimplePublisher*, string, SAL_processingcluster);
	static void processingcluster_abort(int, int, os_time, SimplePublisher*, string, SAL_processingcluster);
	static void processingcluster_enterControl(int, int, os_time, SimplePublisher*, string, SAL_processingcluster);
	static void processingcluster_exitControl(int, int, os_time, SimplePublisher*, string, SAL_processingcluster);

	static string get_next_timed_ack_id(string ack_type); 
};
