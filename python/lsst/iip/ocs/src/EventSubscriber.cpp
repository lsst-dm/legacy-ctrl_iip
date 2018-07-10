#include <string>
#include <sstream>
#include <iostream>
#include <pthread.h>
#include <signal.h>
#include "SAL_camera.h"
#include "SAL_atcamera.h"
#include "SAL_efd.h"
#include "ccpp_sal_camera.h"
#include "ccpp_sal_atcamera.h"
#include "ccpp_sal_efd.h"
#include "os.h"
#include <yaml-cpp/yaml.h>
#include <stdlib.h>

#include "SimplePublisher.h"
#include "EventSubscriber.h"

using namespace DDS;
using namespace camera;
using namespace atcamera;
using namespace efd;
using namespace YAML; 

typedef void* (*funcptr)(void *args);  

volatile sig_atomic_t isRunning = 1; 

EventSubscriber::EventSubscriber() { 
    Node config_file = LoadFile("../../L1SystemCfg.yaml"); 
    Node root = config_file["ROOT"]; 
    base_broker_addr = root["BASE_BROKER_ADDR"].as<string>(); 
    queue_name = root["OCS"]["OCS_PUBLISH"].as<string>(); 
    total_events = 9;

    setup_events_listeners(); 
    cout << "=== dm EVENT/Telemetry controller ready" << endl; 
}

EventSubscriber::~EventSubscriber() { 
} 

void EventSubscriber::setup_events_listeners() { 

    ostringstream rmq_url1; 
    rmq_url1 << "amqp://EVN_1:EVN_1@" << base_broker_addr; 
    cout << rmq_url1.str() << endl; 
    thread_args1 = new event_args; 
    thread_args1->publish_queue = queue_name; 
    thread_args1->broker_addr = rmq_url1.str(); 
    pthread_create(&evn1, NULL, &EventSubscriber::run_ccs_startIntegration, thread_args1); 
    
    ostringstream rmq_url2; 
    rmq_url2 << "amqp://EVN_2:EVN_2@" << base_broker_addr; 
    cout << rmq_url2.str() << endl; 
    thread_args2 = new event_args; 
    thread_args2->publish_queue = queue_name; 
    thread_args2->broker_addr = rmq_url2.str(); 
    pthread_create(&evn2, NULL, &EventSubscriber::run_ccs_endReadout, thread_args2); 
    
    ostringstream rmq_url3; 
    rmq_url3 << "amqp://EVN_3:EVN_3@" << base_broker_addr; 
    cout << rmq_url3.str() << endl; 
    thread_args3 = new event_args; 
    thread_args3->publish_queue = queue_name; 
    thread_args3->broker_addr = rmq_url3.str(); 
    pthread_create(&evn3, NULL, &EventSubscriber::run_atcamera_startIntegration, thread_args3); 
    
    ostringstream rmq_url4; 
    rmq_url4 << "amqp://EVN_4:EVN_4@" << base_broker_addr; 
    cout << rmq_url4.str() << endl; 
    thread_args4 = new event_args; 
    thread_args4->publish_queue = queue_name; 
    thread_args4->broker_addr = rmq_url4.str(); 
    pthread_create(&evn4, NULL, &EventSubscriber::run_atcamera_endReadout, thread_args4); 
    
    ostringstream rmq_url5; 
    rmq_url5 << "amqp://EVN_5:EVN_5@" << base_broker_addr; 
    cout << rmq_url5.str() << endl; 
    thread_args5 = new event_args; 
    thread_args5->publish_queue = queue_name; 
    thread_args5->broker_addr = rmq_url5.str(); 
    pthread_create(&evn5, NULL, &EventSubscriber::run_efd_largeFileObjectAvailable, thread_args5); 
    
} 


void *EventSubscriber::run_ccs_startIntegration(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_camera mgr = SAL_camera(); 
    camera_logevent_startIntegrationC SALInstance; 

    mgr.salEvent("camera_logevent_startIntegration"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(isRunning) { 
        status = mgr.getEvent_startIntegration(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event startIntegration received = " << endl;
		/** 		
            Emitter msg;
            msg << BeginMap; 
            msg << Key << "MSG_TYPE" << Value << "DMCS_TCS_TARGET"; 
            msg << Key << "RA" << Value << "16"; 
            msg << Key << "DEC" << Value << "27"; 
            msg << Key << "ANGLE" << Value << "33";
            msg << Key << "VISIT_ID" << Value << "visit_123";
	    msg << Key << "TARGET_ID" << Value << "targe_321"; 
            msg << EndMap; 	
	    cout << "ER: " << msg.c_str() << endl; 
            publisher->publish_message(queue, msg.c_str());
		*/ 
        } 
        os_nanoSleep(delay_10ms); 
    }  
    mgr.salShutdown(); 
    delete publisher; 
    cout << "Shutting down Camera StartIntegration" << endl; 
    return 0;
} 

void *EventSubscriber::run_ccs_endReadout(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_camera mgr = SAL_camera(); 
    camera_logevent_endReadoutC SALInstance; 

    mgr.salEvent("camera_logevent_endReadout"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(isRunning) { 
        status = mgr.getEvent_endReadout(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event endReadout received = " << endl;
            Emitter msg; 
            msg << BeginMap; 
            msg << Key << "MSG_TYPE" << Value << "DMCS_END_READOUT"; 
            msg << Key << "IMAGE_ID" << Value << SALInstance.imageName;   
            msg << EndMap; 
            cout << "XXX: " << msg.c_str() << endl;
            publisher->publish_message(queue, msg.c_str());
        } 
        os_nanoSleep(delay_10ms); 
    }  
    mgr.salShutdown(); 
    delete publisher; 
    cout << "Shutting down Camera EndReadout" << endl; 
    return 0;
} 


/**
void *EventSubscriber::run_ccs_startIntegration(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_camera mgr = SAL_camera(); 
    camera_logevent_startIntegrationC SALInstance; 

    mgr.salEvent("camera_logevent_startIntegration"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(isRunning) { 
        status = mgr.getEvent_startIntegration(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event dmcs_endreadout received = " << endl;
            ostringstream msg; 
            msg << "{ MSG_TYPE: DMCS_END_READOUT" 
                << ", IMAGE_ID: " << SALInstance.imageName << "}"; 
            cout << "XXX " << msg.str() << endl;
            publisher->publish_message(queue, msg.str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    return 0;
} 
*/ 
void *EventSubscriber::run_tcs_target(void *args) { 
    /** 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
    os_time delay_10ms = { 0, 10000000 };

    int cmdId = -1;
    tcs_command_targetC SALInstance;
    SAL_tcs mgr = SAL_tcs();

    mgr.salProcessor("tcs_command_target");
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while (1) {
        cmdId = mgr.acceptCommand_target(&SALInstance);
        if (cmdId > 0) {
            cout << "=== tcs command target received = " << endl;

            ostringstream msg; 
            msg << " { MSG_TYPE: DMCS_TCS_TARGET" 
                << ", TARGET_ID: " << SALInstance.targetId
                << ", FIELD_ID: " << SALInstance.fieldId
                << ", GROUP_ID: " << SALInstance.groupId
                << ", FILTER: " << SALInstance.filter
                << ", REQUEST_TIME: " << SALInstance.requestTime
                << ", RA: " << SALInstance.ra
                << ", DEC: " << SALInstance.dec
                << ", ANGLE: " << SALInstance.angle
                << ", NUM_EXPOSURES: " << SALInstance.num_exposures
                << ", EXPOSURE_TIMES: " << SALInstance.exposure_times
                << ", SLEW_TIME: " << SALInstance.slew_time << "}";

            publisher->publish_message(queue, msg.str());
        }       
        os_nanoSleep(delay_10ms);
    }
    mgr.salShutdown();
    return 0;
    */ 
} 


void *EventSubscriber::run_atcamera_startIntegration(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_atcamera mgr = SAL_atcamera(); 
    atcamera_logevent_startIntegrationC SALInstance; 

    mgr.salEvent("atcamera_logevent_startIntegration"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(isRunning) { 
        status = mgr.getEvent_startIntegration(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event DMCS_AT_START_INTEGRATION received = " << endl;
            Emitter msg; 
            msg << BeginMap; 
            msg << Key << "MSG_TYPE" << Value << "DMCS_AT_START_INTEGRATION"; 
            msg << Key << "IMAGE_ID" << Value << SALInstance.imageName; 
            msg << Key << "IMAGE_INDEX" << Value << SALInstance.imageIndex; 
            msg << Key << "IMAGE_SEQUENCE_NAME" << Value << SALInstance.imageSequenceName; 
            msg << Key << "IMAGES_IN_SEQUENCE" << Value << SALInstance.imagesInSequence; 
            msg << EndMap; 
	    cout << "msg is: " << endl; 
            cout << msg.c_str() << endl; 
            publisher->publish_message(queue, msg.c_str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    delete publisher; 
    cout << "Shutting down AtCamera StartIntegration" << endl; 
    return 0;
} 

void *EventSubscriber::run_atcamera_endReadout(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_atcamera mgr = SAL_atcamera(); 
    atcamera_logevent_endReadoutC SALInstance; 

    mgr.salEvent("atcamera_logevent_endReadout"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(isRunning) { 
        status = mgr.getEvent_endReadout(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event DMCS_AT_END_READOUT received = " << endl;
            Emitter msg; 
            msg << BeginMap; 
            msg << Key << "MSG_TYPE" << Value << "DMCS_AT_END_READOUT"; 
            msg << Key << "IMAGE_ID" << Value << SALInstance.imageName; 
            msg << Key << "IMAGE_INDEX" << Value << SALInstance.imageIndex; 
            msg << Key << "IMAGE_SEQUENCE_NAME" << Value << SALInstance.imageSequenceName; 
            msg << Key << "IMAGES_IN_SEQUENCE" << Value << SALInstance.imagesInSequence; 
            msg << EndMap; 
            cout << "msg is: " << endl; 
            cout << msg.c_str() << endl; 
            publisher->publish_message(queue, msg.c_str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    delete publisher; 
    cout << "Shutting down AtCamera EndReadout" << endl; 
    return 0;
} 

void *EventSubscriber::run_efd_largeFileObjectAvailable(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_efd mgr = SAL_efd(); 
    efd_logevent_LargeFileObjectAvailableC SALInstance; 

    mgr.salEvent("efd_logevent_LargeFileObjectAvailable"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(isRunning) { 
        status = mgr.getEvent_LargeFileObjectAvailable(&SALInstance); 

        if (status == SAL__OK) { 
            string device = SALInstance.Generator; 
            string msg_type; 
            if (device == "AT") { 
                cout << "=== Event AuxTel HeaderService received = " << endl;
                msg_type = "DMCS_AT_HEADER_READY"; 
            } 
            else { 
                cout << "=== Event Regular HeaderService received = " << endl;
                msg_type = "DMCS_HEADER_READY"; 
            } 

            Emitter msg;
            msg << BeginMap; 
            msg << Key << "MSG_TYPE" << Value << msg_type; 
            msg << Key << "FILENAME" << Value << SALInstance.URL; 
            msg << Key << "IMAGE_ID" << Value << SALInstance.ID; 
            msg << EndMap; 	

	    cout << "msg is: " << endl; 
            cout << msg.c_str() << endl; 
            publisher->publish_message(queue, msg.c_str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    delete publisher; 
    cout << "Shutting down EFD LargeFileObjectAvailable" << endl; 
    return 0;
} 

void EventSubscriber::shutdown() { 
    int status; 
    pthread_join(evn1, (void **)&status); 
    pthread_join(evn2, (void **)&status); 
    pthread_join(evn3, (void **)&status); 
    pthread_join(evn4, (void **)&status); 
    pthread_join(evn5, (void **)&status); 
    
    delete thread_args1;  
    delete thread_args2;  
    delete thread_args3;  
    delete thread_args4;  
    delete thread_args5;  
} 

void signal_handler(int status_code) {
    cout << "Handling keyboard interrupts" << endl; 
    isRunning = 0; 
} 

int main() { 
    EventSubscriber event; 
    signal(SIGINT, signal_handler); 
    signal(SIGTERM, signal_handler); 
    while(isRunning) { 

    } 
    event.shutdown(); 
    return 0; 
} 
