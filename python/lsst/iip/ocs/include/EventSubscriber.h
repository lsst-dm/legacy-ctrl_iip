class EventSubscriber { 
    public: 
        struct event_args { 
            string publish_queue; 
            string broker_addr; 
        }; 

        event_args *thread_args; 
        
        EventSubscriber(); 
        ~EventSubscriber();

        string base_broker_addr; 
        string queue_name; 

        void setup_events_listeners(); 

        static void *run_ccs_takeImages(void*); 
        static void *run_ccs_startIntegration(void*); 
        static void *run_ccs_startReadout(void*); 
        static void *run_ccs_endReadout(void*); 
        static void *run_ccs_startShutterOpen(void*); 
        static void *run_ccs_startShutterClose(void*); 
        static void *run_ccs_endShutterOpen(void*); 
        static void *run_ccs_endShutterClose(void*); 
        static void *run_tcs_target(void*); 
        static void *run_targetVisitAccept(void*);
        static void *run_targetVisitDone(void*);
        static void *run_takeImageDone  (void*);
}; 
