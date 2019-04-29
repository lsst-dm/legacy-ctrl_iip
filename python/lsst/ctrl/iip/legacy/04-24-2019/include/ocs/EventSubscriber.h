#include "IIPBase.h"

class EventSubscriber : public IIPBase { 
    public: 
        struct event_args { 
            string publish_queue; 
            string broker_addr; 
        }; 

        event_args *thread_args; 
        
        EventSubscriber(); 
        ~EventSubscriber();

        int total_events;

        void setup_events_listeners(); 

        static void *run_ccs_takeImages(void*); 
        static void *run_ccs_startIntegration(void*); 
        static void *run_ccs_endReadout(void*); 
        static void *run_tcs_target(void*); 
        static void *run_takeImageDone(void*);
        static void *run_getHeaderService(void*);

        static void *run_atcamera_startIntegration(void *); 
        static void *run_atcamera_endReadout(void *); 
        static void *run_efd_largeFileObjectAvailable(void *); 
}; 
