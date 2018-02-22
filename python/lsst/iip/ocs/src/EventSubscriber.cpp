#include <string>
#include <sstream>
#include <iostream>
#include <pthread.h>
#include "SAL_archiver.h" // for fake guys
#include "SAL_camera.h"
#include "SAL_tcs.h"
#include "SAL_dmHeaderService.h"
#include "ccpp_sal_camera.h"
#include "ccpp_sal_tcs.h"
#include "ccpp_sal_dmHeaderService.h"
#include "os.h"
#include <yaml-cpp/yaml.h>
#include <stdlib.h>

#include "SimplePublisher.h"
#include "EventSubscriber.h"

using namespace DDS;
using namespace camera;
using namespace tcs; 
using namespace YAML; 

typedef void* (*funcptr)(void *args);  

EventSubscriber::EventSubscriber() { 
    Node config_file = LoadFile("../../L1SystemCfg.yaml"); 
    Node root = config_file["ROOT"]; 
    base_broker_addr = root["BASE_BROKER_ADDR"].as<string>(); 
    queue_name = root["OCS"]["OCS_PUBLISH"].as<string>(); 

    setup_events_listeners(); 
    cout << "=== dm EVENT/Telemetry controller ready" << endl; 
}

EventSubscriber::~EventSubscriber() { 
} 

void EventSubscriber::setup_events_listeners() { 
    int thread_counts = 13; 
    funcptr thread_funcs[] {  &EventSubscriber::run_ccs_takeImages, 
                               &EventSubscriber::run_ccs_startIntegration, 
                               &EventSubscriber::run_ccs_startReadout, 
                               &EventSubscriber::run_ccs_endReadout, 
                               &EventSubscriber::run_ccs_startShutterOpen, 
                               &EventSubscriber::run_ccs_startShutterClose, 
                               &EventSubscriber::run_ccs_endShutterOpen, 
                               &EventSubscriber::run_ccs_endShutterClose, 
                               &EventSubscriber::run_tcs_target, 
                               &EventSubscriber::run_targetVisitAccept, 
                               &EventSubscriber::run_targetVisitDone, 
                               &EventSubscriber::run_takeImageDone,
                               &EventSubscriber::run_getHeaderService};
    
    for (int i = 0; i < thread_counts; i++) { 
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
*/

void *EventSubscriber::run_ccs_startReadout(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
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

/**
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
            ostringstream msg; 
            msg << "{ MSG_TYPE: CCS_END_READOUT }"; 
            publisher->publish_message(queue, msg.str());
        } 
        os_nanoSleep(delay_10ms); 
    }  
    mgr.salShutdown(); 
    return 0;
} 
*/ 

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

void *EventSubscriber::run_ccs_startShutterOpen(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
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
            msg << "{ MSG_TYPE: CCS_START_SHUTTER_OPEN }"; 
            publisher->publish_message(queue, msg.str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    return 0;
} 

void *EventSubscriber::run_ccs_startShutterClose(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
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
            msg << "{ MSG_TYPE: CCS_START_SHUTTER_CLOSE }"; 
            publisher->publish_message(queue, msg.str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    return 0;
} 

void *EventSubscriber::run_ccs_endShutterOpen(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
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

void *EventSubscriber::run_ccs_endShutterClose(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
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
void *EventSubscriber::run_tcs_target(void *args) { 
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
} 

// FAKE GUYS 
void *EventSubscriber::run_targetVisitAccept(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_archiver mgr = SAL_archiver(); 
    archiver_logevent_targetVisitAcceptC SALInstance; 

    mgr.salEvent("archiver_logevent_targetVisitAccept"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_targetVisitAccept(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event targetVisitAccept received = " << endl;
            ostringstream msg; 
            msg << "{ MSG_TYPE: TARGET_VISIT_ACCEPT }"; 
            publisher->publish_message(queue, msg.str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    return 0;
} 

void *EventSubscriber::run_targetVisitDone(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_archiver mgr = SAL_archiver(); 
    archiver_logevent_targetVisitDoneC SALInstance; 

    mgr.salEvent("archiver_logevent_targetVisitDone"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_targetVisitDone(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event targetVisitDone received = " << endl;
            ostringstream msg; 
            msg << "{ MSG_TYPE: TARGET_VISIT_DONE }"; 
            publisher->publish_message(queue, msg.str()); 
        } 
        os_nanoSleep(delay_10ms);
    }  
    mgr.salShutdown(); 
    return 0;
} 

void *EventSubscriber::run_takeImageDone(void *args) { 
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
} 
            
void *EventSubscriber::run_getHeaderService(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_dmHeaderService mgr = SAL_dmHeaderService(); 
    dmHeaderService_logevent_LargeFileObjectAvailableC SALInstance; 

    mgr.salEvent("dmHeaderService_logevent_LargeFileObjectAvailable"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_LargeFileObjectAvailable(&SALInstance); 

        if (status == SAL__OK) { 
            cout << "=== Event HeaderService received = " << endl;
            string path = SALInstance.URL; 
            size_t found = path.find_last_of("/"); 
            string file_name = path.substr(found+1); 

            size_t dot = file_name.find_last_of("."); 
            string img_id = file_name.substr(0, dot); 

            ostringstream msg; 
            msg << "{ MSG_TYPE: HEADER_READY"
                << ", IMG_ID: " << img_id << "}"; 
            publisher->publish_message(queue, msg.str()); 
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
