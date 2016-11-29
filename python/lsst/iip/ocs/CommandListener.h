class CommandListener : public OCS_Bridge { 
    public: 
	struct ocs_thread_args { 
	    SAL_dm dmgr; 
	    AmqpClient::Channel::ptr_t ocsAmqp; 
	    string q; 
	}; 
	ocs_thread_args *command_args;
	SAL_dm mgr; 
	pthread_t ocsthread; 

	CommandListener(string); 
	~CommandListener();
	void setup_ocs_consumer(); 
	static void *run_ocs_consumer(void *); 
	static void dm_start(int, int, os_time, AmqpClient::Channel::ptr_t, string, SAL_dm);
	static void dm_stop(int, int, os_time, AmqpClient::Channel::ptr_t, string, SAL_dm);
	static void dm_enable(int, int, os_time, AmqpClient::Channel::ptr_t, string, SAL_dm);
	static void dm_disable(int, int, os_time, AmqpClient::Channel::ptr_t, string, SAL_dm);
	static void dm_enterControl(int, int, os_time, AmqpClient::Channel::ptr_t, string, SAL_dm);
	static void dm_standby(int, int, os_time, AmqpClient::Channel::ptr_t, string, SAL_dm);
	static void dm_exitControl(int, int, os_time, AmqpClient::Channel::ptr_t, string, SAL_dm);
        static void dm_abort(int, int, os_time, AmqpClient::Channel::ptr_t, string, SAL_dm); 
};
