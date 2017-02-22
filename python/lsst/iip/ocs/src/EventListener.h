class EventListener : public OCS_Bridge { 
    public: 
	struct ocs_thread_args { 
	    SAL_dm dmgr; 
	    SimplePublisher* publisher; 
	    string q; 
	}; 
	ocs_thread_args *command_args;
	SAL_dm mgr; 

	EventListener(); 
	~EventListener();
	void run(); 
	void log_readout(string); 
	void log_next_visit(string); 
	void log_start_integration(string); 
};
