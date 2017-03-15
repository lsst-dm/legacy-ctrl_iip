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
	    SAL_dm dmgr; 
	    SimplePublisher* publisher; 
	    string q; 
	}; 

        /** ocs command arguements to pass to pthread */ 
	ocs_thread_args *command_args;
 
        /** SAL dm manager to listen to messages from DDS */ 
	SAL_dm mgr; 

        /** pthread to listen to messages in the background */ 
	pthread_t ocsthread; 

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
	static void dm_start(int, int, os_time, SimplePublisher*, string, SAL_dm);

        /** dm_stop is used in run_ocs_consumer to accept messages from OCS system via device called stop_commander
          * @param cmdId command id issued by the SAL
          * @param timeout timeout to use with the controller
          * @param delay_10ms delay milliseconds
          * @param publisher publisher object to send messages to Rabbitmq 
          * @param queue queue name to send messages to 
          * @param mgr SAL_dm manager to handle acceptance of messages from OCS
          */ 
	static void dm_stop(int, int, os_time, SimplePublisher*, string, SAL_dm);

        /** dm_enable is used in run_ocs_consumer to accept messages from OCS system via device called enable_commander
          * @param cmdId command id issued by the SAL
          * @param timeout timeout to use with the controller
          * @param delay_10ms delay milliseconds
          * @param publisher publisher object to send messages to Rabbitmq 
          * @param queue queue name to send messages to 
          * @param mgr SAL_dm manager to handle acceptance of messages from OCS
          */ 
	static void dm_enable(int, int, os_time, SimplePublisher*, string, SAL_dm);

        /** dm_disable is used in run_ocs_consumer to accept messages from OCS system via device called disable_commander
          * @param cmdId command id issued by the SAL
          * @param timeout timeout to use with the controller
          * @param delay_10ms delay milliseconds
          * @param publisher publisher object to send messages to Rabbitmq 
          * @param queue queue name to send messages to 
          * @param mgr SAL_dm manager to handle acceptance of messages from OCS
          */ 
	static void dm_disable(int, int, os_time, SimplePublisher*, string, SAL_dm);

        /** dm_enterControl is used in run_ocs_consumer to accept messages from OCS system via device called enterControl_commander
          * @param cmdId command id issued by the SAL
          * @param timeout timeout to use with the controller
          * @param delay_10ms delay milliseconds
          * @param publisher publisher object to send messages to Rabbitmq 
          * @param queue queue name to send messages to 
          * @param mgr SAL_dm manager to handle acceptance of messages from OCS
          */ 
	static void dm_enterControl(int, int, os_time, SimplePublisher*, string, SAL_dm);

        /** dm_standby is used in run_ocs_consumer to accept messages from OCS system via device called standby_commander
          * @param cmdId command id issued by the SAL
          * @param timeout timeout to use with the controller
          * @param delay_10ms delay milliseconds
          * @param publisher publisher object to send messages to Rabbitmq 
          * @param queue queue name to send messages to 
          * @param mgr SAL_dm manager to handle acceptance of messages from OCS
          */ 
	static void dm_standby(int, int, os_time, SimplePublisher*, string, SAL_dm);

        /** dm_exitControl is used in run_ocs_consumer to accept messages from OCS system via device called exitControl_commander
          * @param cmdId command id issued by the SAL
          * @param timeout timeout to use with the controller
          * @param delay_10ms delay milliseconds
          * @param publisher publisher object to send messages to Rabbitmq 
          * @param queue queue name to send messages to 
          * @param mgr SAL_dm manager to handle acceptance of messages from OCS
          */ 
	static void dm_exitControl(int, int, os_time, SimplePublisher*, string, SAL_dm);

        /** dm_abort is used in run_ocs_consumer to accept messages from OCS system via device called abort_commander
          * @param cmdId command id issued by the SAL
          * @param timeout timeout to use with the controller
          * @param delay_10ms delay milliseconds
          * @param publisher publisher object to send messages to Rabbitmq 
          * @param queue queue name to send messages to 
          * @param mgr SAL_dm manager to handle acceptance of messages from OCS
          */ 
        static void dm_abort(int, int, os_time, SimplePublisher*, string, SAL_dm); 
};
