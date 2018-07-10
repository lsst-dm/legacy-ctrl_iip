class EventSubscriber { 
    public: 
        struct event_args { 
            string publish_queue; 
            string broker_addr; 
        }; 

        event_args *thread_args1, *thread_args2, *thread_args3, *thread_args4, *thread_args5; 
        pthread_t evn1, evn2, evn3, evn4, evn5; 
        
        EventSubscriber(); 
        ~EventSubscriber();

        string base_broker_addr; 
        string queue_name; 
        int total_events;

        void setup_events_listeners(); 

        // static void *run_ccs_takeImages(void*); 
        static void *run_ccs_startIntegration(void*); 
        static void *run_ccs_endReadout(void*); 
        static void *run_tcs_target(void*); 
        // static void *run_takeImageDone(void*);
        // static void *run_getHeaderService(void*);

        static void *run_atcamera_startIntegration(void *); 
        static void *run_atcamera_endReadout(void *); 
        static void *run_efd_largeFileObjectAvailable(void *); 

        void shutdown(); 
}; 
