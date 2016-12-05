class EventListener : public OCS_Bridge { 
    public: 
	struct ocs_thread_args { 
	    SAL_dm dmgr; 
	    AmqpClient::Channel::ptr_t ocsAmqp; 
	    string q; 
	}; 
	ocs_thread_args *command_args;
	pthread_t publishT; 
	pthread_t archiveT;
	string cmdEntity;
	SAL_dm mgr; 

	EventListener(string); 
	~EventListener();
	void run(); 
	void log_readout(string); 
	void log_next_visit(string); 
	void log_start_integration(string); 
};
