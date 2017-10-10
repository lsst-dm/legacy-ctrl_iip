#include <string>
#include <sstream>
#include <iostream>
#include "SAL_camera.h"
#include "ccpp_sal_camera.h"
#include "os.h"
#include <stdlib.h>

#include "example_main.h"
#include "SimplePublisher.h"

using namespace DDS;
using namespace camera;
using namespace YAML; 


EventSubscriber::EventSubscriber() { 
    // OCS_Bridge SimplePublisher needs to be new.
    Node root = 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 
    setup_events_controllers(); 

    cout << "=== dm EVENT/Telemetry controller ready" << endl; 
}

EventSubscriber::~EventSubscriber() { 
} 

void EventSubscriber::setup_events_listeners() { 
    pthread takeImages, startIntegration, startReadout, endReadout, 
            startShutterOpen, startShutterClose, endShutterOpen, endShutterClose, schedulerTarget;  

    // TODO: add arguments to these threads.
    pthread_create(&takeImages, NULL, &EventListener::run_ccs_takeImages, NULL); 
    pthread_create(&startIntegration, NULL, &EventListener::run_ccs_startIntegration, NULL); 
    pthread_create(&startReadout, NULL, &EventListener::run_ccs_startReadout, NULL); 
    pthread_create(&endReadout, NULL, &EventListener::run_ccs_endReadout, NULL); 
    pthread_create(&startShutterOpen, NULL, &EventListener::run_ccs_startShutterOpen, NULL); 
    pthread_create(&startShutterClose, NULL, &EventListener::run_ccs_startShutterClose, NULL); 
    pthread_create(&endShutterOpen, NULL, &EventListener::run_ccs_endShutterOpen, NULL); 
    pthread_create(&endShutterClose, NULL, &EventListener::run_ccs_endShutterClose, NULL); 
    pthread_create(&schedulerTarget, NULL, &EventListener::run_tcs_target, NULL); 
} 

void *EventListener::run_ccs_takeImages(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; // USERNAME
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_camera mgr = SAL_camera(); 
    camera_camera_takeImagesC SALInstance; 

    mgr.salProcessor("camera_command_takeImages"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.acceptCommand_takeImages(&SALInstance); 

        if (status > 0) { 
            cout << "## Command takeImages Received." << endl; 
            ostringstream msg; 
            msg << "{ MSG_TYPE: CCS_TAKE_IMAGES"
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

void *EventListener::run_ccs_startIntegration(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; // USERNAME
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_camera mgr = SAL_camera(); 
    camera_logevent_startIntegrationC SALInstance; 

    mgr.salEvent("camera_logevent_startIntegration"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_startIntegration(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event startIntegration Received =" << endl; 
            ostringstream msg; 
            msg << "{ MSG_TYPE: CCS_START_INTEGRATION"
                << ", IMAGE_NAME: " << SALInstance.imageName  << "}"; 
            publisher->publish_message(queue, msg.str());
        } 
        os_nanoSleep(delay_10ms); 
    }  
    mgr.salShutdown(); 
    return 0;
} 

void *EventListener::run_ccs_startReadout(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; // USERNAME
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_camera mgr = SAL_camera(); 
    camera_logevent_startReadoutC SALInstance; 

    mgr.salEvent("camera_logevent_startReadout"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_startReadout(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event startReadout received = " << endl;
            ostringstream msg; 
            msg << "{ MSG_TYPE: CCS_START_READOUT}"; 
            publisher->publish_message(queue, msg.str()); 
        } 
        os_nanoSleep(delay_10ms); 
    }  
    mgr.salShutdown(); 
    return 0;
} 

void *EventListener::run_ccs_endReadout(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; // USERNAME
 
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
            ostringstream msg; 
            msg << "{ MSG_TYPE: CCS_END_READOUT }"; 
            publisher->publish_message(queue, msg.str());
        } 
        os_nanoSleep(delay_10ms); 
    }  
    mgr.salShutdown(); 
    return 0;
} 

void *EventListener::run_ccs_startShutterOpen(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; // USERNAME
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_camera mgr = SAL_camera(); 
    camera_logevent_startShutterOpenC SALInstance; 

    mgr.salEvent("camera_logevent_startShutterOpen"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_startShutterOpen(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event startShutterOpen received = " << endl;
            ostringstream msg; 
            msg << "{ MSG_TYPE: CCS_SHUTTER_OPEN }"; 
            publisher->publish_message(queue, msg.str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    return 0;
} 

void *EventListener::run_ccs_startShutterClose(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; // USERNAME
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_camera mgr = SAL_camera(); 
    camera_logevent_startShutterCloseC SALInstance; 

    mgr.salEvent("camera_logevent_startShutterClose"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_startShutterClose(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event startShutterClose received = " << endl;
            ostringstream msg; 
            msg << "{ MSG_TYPE: CCS_SHUTTER_CLOSE }"; 
            publisher->publish_message(queue, msg.str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    return 0;
} 

void *EventListener::run_ccs_endShutterOpen(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; // USERNAME
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_camera mgr = SAL_camera(); 
    camera_logevent_endShutterOpenC SALInstance; 

    mgr.salEvent("camera_logevent_endShutterOpen"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_endShutterOpen(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event endShutterOpen received = " << endl;
            ostringstream msg; 
            msg << "{ MSG_TYPE: CCS_END_SHUTTER_OPEN }"; 
            publisher->publish_message(queue, msg.str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    return 0;
} 

void *EventListener::run_ccs_endShutterClose(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; // USERNAME
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_camera mgr = SAL_camera(); 
    camera_logevent_endShutterCloseC SALInstance; 

    mgr.salEvent("camera_logevent_endShutterClose"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_endShutterClose(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event endShutterClose received = " << endl;
            ostringstream msg; 
            msg << "{ MSG_TYPE: CCS_END_SHUTTER_CLOSE }"; 
            publisher->publish_message(queue, msg.str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    return 0;
} 

void *EventListener::run_tcs_target(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; // USERNAME
    os_time delay_10ms = { 0, 10000000 };

    int cmdId = -1;
    tcs_command_targetC SALInstance;
    SAL_tcs mgr = SAL_tcs();

    mgr.salProcessor("tcs_command_target");
    SimplePublisher *publisher = new SimplePubisher(broker_addr); 

    while (1) {
        cmdId = mgr.acceptCommand_target(&SALInstance);
        if (cmdId > 0) {
            cout << "=== tcs command target received = " << endl;

            ostringstream msg; 
            msg << " { MSG_TYPE: TCS_TARGET" 
            << ", TARGETiD : " << SALInstance.targetId;
            << ", FIELDiD : " << SALInstance.fieldId;
            << ", GROUPiD : " << SALInstance.groupId;
            << ", FILTER : " << SALInstance.filter;
            << ", REQUESTtIME : " << SALInstance.requestTime;
            << ", RA : " << SALInstance.ra;
            << ", DEC : " << SALInstance.dec;
            << ", ANGLE : " << SALInstance.angle;
            << ", NUM_EXPOSURES : " << SALInstance.num_exposures;
            << ", EXPOSURE_TIMES : " << SALInstance.exposure_times;
            << ", SLEW_TIME : " << SALInstance.slew_time << "}";

            publisher->publish_message(queue, msg.str());
        }       
        os_nanoSleep(delay_10ms);
    }
    mgr.salShutdown();
    return 0;
} 



