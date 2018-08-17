#include <string>
#include <sstream>
#include <iostream>
#include <pthread.h>
#include "SAL_camera.h"
#include "SAL_atcamera.h"
#include "SAL_efd.h"
#include "SAL_atHeaderService.h"
#include "ccpp_sal_camera.h"
#include "ccpp_sal_atcamera.h"
#include "ccpp_sal_efd.h"
#include "ccpp_sal_atHeaderService.h"
#include "os.h"
#include <yaml-cpp/yaml.h>
#include <stdlib.h>

#include "SimplePublisher.h"
#include "EventSubscriber.h"

using namespace DDS;
using namespace camera;
using namespace atcamera;
using namespace efd;
using namespace atHeaderService;
using namespace YAML; 

typedef void* (*funcptr)(void *args);  

// To disable efd message, comment out line 503, where `publisher->publish_message`.
// To disable atHeader message, comment out line 385, where `publisher->publish_message`.
// What this means is that EventSubscriber might get message from both, but only publish message from the correct CSC.

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
    funcptr thread_funcs[] {   &EventSubscriber::run_ccs_takeImages, 
                               &EventSubscriber::run_ccs_startIntegration, 
                               &EventSubscriber::run_ccs_endReadout, 
                               &EventSubscriber::run_tcs_target, 
                               &EventSubscriber::run_takeImageDone,
                               &EventSubscriber::run_getHeaderService, 
                               &EventSubscriber::run_atcamera_startIntegration, 
                               &EventSubscriber::run_atcamera_endReadout,
                               &EventSubscriber::run_efd_largeFileObjectAvailable};
    
    for (int i = 0; i < total_events; i++) { 
        ostringstream rmq_url; 
        rmq_url << "amqp://EVN_" << (i+1) << ":EVN_" << (i+1) << "@" << base_broker_addr; 
    
        cout << rmq_url.str() << endl; 
        pthread_t thread; 
        
        thread_args = new event_args; 
        thread_args->publish_queue = queue_name; 
        thread_args->broker_addr = rmq_url.str(); 
        
        pthread_create(&thread, NULL, thread_funcs[i], thread_args); 
    }  
} 

/** 
void *EventSubscriber::run_ccs_takeImages(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_camera mgr = SAL_camera(); 
    camera_command_takeImagesC SALInstance; 

    mgr.salProcessor("camera_command_takeImages"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.acceptCommand_takeImages(&SALInstance); 

        if (status > 0) { 
            cout << "=== Command takeImages Received. =" << endl; 
            ostringstream msg; 
            msg << "{ MSG_TYPE: DMCS_TAKE_IMAGES"
                << ", NUM_IMAGES: " << SALInstance.numImages
                << ", EXP_TIME: " << SALInstance.expTime
                << ", SHUTTER: " << SALInstance.shutter
                << ", SCIENCE: " << SALInstance.science
                << ", GUIDE: " << SALInstance.guide
                << ", WFS: " << SALInstance.wfs
                << ", IMAGE_SEQUENCE_NAME: " << SALInstance.imageSequenceName << "}"; 
            publisher->publish_message(queue, msg.str());
        } 
        os_nanoSleep(delay_10ms); 
    }  
    mgr.salShutdown(); 
    return 0;
} 
*/ 
void *EventSubscriber::run_ccs_takeImages(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_camera mgr = SAL_camera(); 
    camera_command_takeImagesC SALInstance; 

    mgr.salProcessor("camera_command_takeImages"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.acceptCommand_takeImages(&SALInstance); 

        if (status > 0) { 
            cout << "=== Command nextVisit Received. =" << endl; 
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
        } 
        os_nanoSleep(delay_10ms); 
    }  
    mgr.salShutdown(); 
    return 0;
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

    while(1) { 
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

    while(1) { 
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
    return 0;
} 
/** 
void *EventSubscriber::run_ccs_endReadout(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_archiver mgr = SAL_archiver(); 
    archiver_logevent_endReadoutC SALInstance; 

    mgr.salEvent("archiver_logevent_endReadout"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_endReadout(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event endReadout received = " << endl;
            ostringstream msg; 
            msg << "{ MSG_TYPE: DMCS_END_READOUT" 
                << ", IMAGE_ID: " << SALInstance.ImageName << "}"; 
            publisher->publish_message(queue, msg.str());
        } 
        os_nanoSleep(delay_10ms); 
    }  
    mgr.salShutdown(); 
    return 0;
} 
*/


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

    while(1) { 
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

void *EventSubscriber::run_takeImageDone(void *args) { 
    /** 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_archiver mgr = SAL_archiver(); 
    archiver_logevent_takeImageDoneC SALInstance; 

    mgr.salEvent("archiver_logevent_takeImageDone"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_takeImageDone(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event takeImageDone received = " << endl;
            ostringstream msg; 
            msg << "{ MSG_TYPE: DMCS_TAKE_IMAGES_DONE }"; 
            publisher->publish_message(queue, msg.str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    return 0;
    */ 
} 
            
void *EventSubscriber::run_getHeaderService(void *args) { 
/**
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_atHeaderService mgr = SAL_atHeaderService(); 
    atHeaderService_logevent_largeFileObjectAvailableC SALInstance; 

    mgr.salEvent("atHeaderService_logevent_largeFileObjectAvailable"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_largeFileObjectAvailable(&SALInstance); 

        if (status == SAL__OK) { 
            string device = SALInstance.generator; 
            string msg_type; 
            if (device == "atHeaderService") { 
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
            msg << Key << "FILENAME" << Value << SALInstance.url; 
            msg << Key << "IMAGE_ID" << Value << SALInstance.id; 
            msg << EndMap; 	

	    cout << "msg is: " << endl; 
            cout << msg.c_str() << endl; 
            publisher->publish_message(queue, msg.c_str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
*/
    return 0;
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

    while(1) { 
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

    while(1) { 
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
    return 0;
} 

void *EventSubscriber::run_efd_largeFileObjectAvailable(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_efd mgr = SAL_efd(); 
    efd_logevent_largeFileObjectAvailableC SALInstance; 

    mgr.salEventSub("efd_logevent_largeFileObjectAvailable"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_largeFileObjectAvailable(&SALInstance); 

        if (status == SAL__OK) { 
            string device = SALInstance.generator; 
            string msg_type; 
	    cout << "Generator is " << device << endl; 
            if (device == "atHeaderService") { 
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
            msg << Key << "FILENAME" << Value << SALInstance.url; 
            msg << Key << "IMAGE_ID" << Value << SALInstance.id; 
            msg << EndMap; 	

	    cout << "msg is: " << endl; 
            cout << msg.c_str() << endl; 
            publisher->publish_message(queue, msg.c_str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    return 0;
} 

int main() { 
    EventSubscriber event; 
    while(1) { 

    } 
    return 0; 
} 
