/** EventListener listens to event commands such as next_visit, start_integration commands from SAL.
  * It extends OCS_Bridge which handles Config file opening and setting up Rabbit publisher.
  */ 
class EventListener : public OCS_Bridge { 
    public: 
        /** ocs thread arguments to pass to the pthread
          * @dmgr SAL_dm manager object to construct DDS message sender
          * @publisher SimplePublisher rabbitmq object to send messages 
          * @q queue name to listen to messages from DMCS
          */ 
	struct ocs_thread_args { 
	    SAL_dm dmgr; 
	    SimplePublisher* publisher; 
	    string q; 
	}; 

        /** ocs thread struct object to send to pthread */ 
	ocs_thread_args *command_args;
        
        /** SAL dm manager to constrcut DDS message sender */ 
	SAL_dm mgr; 

        /** constructor for EventListener object */ 
	EventListener(); 

        /* destructor for EventListener */
	~EventListener();
 
        /** run method is called whenever Event Listener runs. It handles messages by chopping off string
          * sent by OCS and calls action handler to publish messages.
          */ 
	void run(); 

        /** handles readout message type and publishes to OCS_PUBLISH queue
          * @param message message string which looks like a python dictionary '{"MSG_TYPE": ... }'
          */ 
	void log_readout(string); 

        /** handles next_visit message type and publishes to OCS_PUBLISH queue
          * @param message message string which looks like a python dictionary '{"MSG_TYPE": ... }'
          */ 
	void log_next_visit(string); 

        /** handles start_integration message type and publishes to OCS_PUBLISH queue
          * @param message message string which looks like a python dictionary '{"MSG_TYPE": ... }'
          */ 
	void log_start_integration(string); 
};
