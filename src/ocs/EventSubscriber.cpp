/*
 * This file is part of ctrl_iip
 *
 * Developed for the LSST Data Management System.
 * This product includes software developed by the LSST Project
 * (https://www.lsst.org).
 * See the COPYRIGHT file at the top-level directory of this distribution
 * for details of code ownership.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include <string>
#include <sstream>
#include <iostream>
#include <pthread.h>
#include <yaml-cpp/yaml.h>
#include <stdlib.h>
#include "SAL_MTCamera.h"
#include "SAL_ATCamera.h"
#include "SAL_EFD.h"
#include "ccpp_sal_MTCamera.h"
#include "ccpp_sal_ATCamera.h"
#include "ccpp_sal_EFD.h"

#include "EventSubscriber.h"
#include "Toolsmod.h"
#include "SimplePublisher.h"

BOOST_LOG_INLINE_GLOBAL_LOGGER_DEFAULT(lg, src::severity_logger_mt< severity_level >);
#include "IIPMacro.h"


using namespace DDS;
using namespace MTCamera;
using namespace ATCamera;
using namespace EFD;
using namespace YAML; 

typedef void* (*funcptr)(void *args);  

EventSubscriber::EventSubscriber() : IIPBase("L1SystemCfg.yaml", "EventSubscriber") { 
    this->total_events = 9;

    setup_events_listeners(); 
    LOG_DBG << "=== dm EVENT/Telemetry controller ready"; 
}

EventSubscriber::~EventSubscriber() { 
} 

void EventSubscriber::setup_events_listeners() { 
    funcptr thread_funcs[] {   
        &EventSubscriber::run_ccs_takeImages, 
        &EventSubscriber::run_ccs_startIntegration, 
        &EventSubscriber::run_ccs_endReadout, 
        &EventSubscriber::run_tcs_target, 
        &EventSubscriber::run_takeImageDone,
        &EventSubscriber::run_getHeaderService, 
        &EventSubscriber::run_atcamera_startIntegration, 
        &EventSubscriber::run_atcamera_endReadout, 
        &EventSubscriber::run_efd_largeFileObjectAvailable
    };
    
    Node ocs;
    string user, passwd, base_addr, publishq;
    try { 
        ocs = this->config_root["OCS"];
        user = this->credentials->get_user("service_user");
        passwd = this->credentials->get_passwd("service_passwd");
	base_addr = this->config_root["BASE_BROKER_ADDR"].as<string>(); 
        publishq = this->config_root["OCS"]["OCS_PUBLISH"].as<string>(); 
    }
    catch (YAML::TypedBadConversion<string>& e) { 
	LOG_CRT << "Cannot read ocs fields from L1SystemCfg.yaml"; 
	exit(-1); 
    }
    
    string amqp_url = this->get_amqp_url(user, passwd, base_addr);
    for (int i = 0; i < this->total_events; i++) { 
        pthread_t thread; 
        thread_args = new event_args; 
        thread_args->publish_queue = publishq; 
        thread_args->broker_addr = amqp_url; 
        pthread_create(&thread, NULL, thread_funcs[i], thread_args); 
    }  
} 

void *EventSubscriber::run_ccs_takeImages(void *args) { 
    event_args *params = ((event_args *)args); 
    string queue = params->publish_queue; 
    string broker_addr = params->broker_addr; 
 
    os_time delay_10ms = { 0, 10000000 };
    int status = -1; 
    SAL_MTCamera mgr = SAL_MTCamera(); 
    MTCamera_command_takeImagesC SALInstance; 

    mgr.salProcessor("MTCamera_command_takeImages"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.acceptCommand_takeImages(&SALInstance); 

        if (status > 0) { 
            LOG_DBG << "=== Command nextVisit Received. ="; 
            Emitter msg;
            msg << BeginMap; 
            msg << Key << "MSG_TYPE" << Value << "DMCS_TCS_TARGET"; 
            msg << Key << "RA" << Value << "16"; 
            msg << Key << "DEC" << Value << "27"; 
            msg << Key << "ANGLE" << Value << "33";
            msg << Key << "VISIT_ID" << Value << "visit_123";
	    msg << Key << "TARGET_ID" << Value << "targe_321"; 
            msg << EndMap; 	
	    LOG_DBG << "ER: " << msg.c_str(); 
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
    SAL_MTCamera mgr = SAL_MTCamera(); 
    MTCamera_logevent_startIntegrationC SALInstance; 

    mgr.salEvent("MTCamera_logevent_startIntegration"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_startIntegration(&SALInstance); 

        if (status == SAL__OK) { 
            LOG_DBG << "=== Event startIntegration received = ";
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
	    LOG_DBG << "ER: " << msg.c_str(); 
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
    SAL_MTCamera mgr = SAL_MTCamera(); 
    MTCamera_logevent_endReadoutC SALInstance; 

    mgr.salEvent("MTCamera_logevent_endReadout"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_endReadout(&SALInstance); 

        if (status == SAL__OK) { 
            LOG_DBG << "=== Event endReadout received = ";
            Emitter msg; 
            msg << BeginMap; 
            msg << Key << "MSG_TYPE" << Value << "DMCS_END_READOUT"; 
            msg << Key << "IMAGE_ID" << Value << SALInstance.imageName;   
            msg << EndMap; 
            LOG_DBG << "XXX: " << msg.c_str();
            publisher->publish_message(queue, msg.c_str());
        } 
        os_nanoSleep(delay_10ms); 
    }  
    mgr.salShutdown(); 
    return 0;
} 

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
            LOG_DBG << "=== tcs command target received = ";

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
            LOG_DBG << "=== Event takeImageDone received = ";
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
    SAL_headerService mgr = SAL_headerService(); 
    headerService_logevent_LargeFileObjectAvailableC SALInstance; 

    mgr.salEvent("headerService_logevent_LargeFileObjectAvailable"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_LargeFileObjectAvailable(&SALInstance); 

        if (status == SAL__OK) { 
            LOG_DBG << "=== Event HeaderService received = ";
            Emitter msg;
            msg << BeginMap; 
            msg << Key << "MSG_TYPE" << Value << "DMCS_HEADER_READY"; 
            msg << Key << "FILENAME" << Value << SALInstance.URL; 
            msg << EndMap; 	
	    LOG_DBG << "HR: " << msg.c_str(); 
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
    SAL_ATCamera mgr = SAL_ATCamera(); 
    ATCamera_logevent_startIntegrationC SALInstance; 

    mgr.salEvent("ATCamera_logevent_startIntegration"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_startIntegration(&SALInstance); 

        if (status == SAL__OK) { 
            LOG_DBG << "=== Event DMCS_AT_START_INTEGRATION received = ";
            Emitter msg; 
            msg << BeginMap; 
            msg << Key << "MSG_TYPE" << Value << "DMCS_AT_START_INTEGRATION"; 
            msg << Key << "IMAGE_ID" << Value << SALInstance.imageName; 
            msg << Key << "IMAGE_INDEX" << Value << SALInstance.imageIndex; 
            msg << Key << "IMAGE_SEQUENCE_NAME" << Value << SALInstance.imageSequenceName; 
            msg << Key << "IMAGES_IN_SEQUENCE" << Value << SALInstance.imagesInSequence; 
            msg << EndMap; 
	    LOG_DBG << "Published msg is: " << msg.c_str(); 
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
    SAL_ATCamera mgr = SAL_ATCamera(); 
    ATCamera_logevent_endReadoutC SALInstance; 

    mgr.salEvent("ATCamera_logevent_endReadout"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_endReadout(&SALInstance); 

        if (status == SAL__OK) { 
            LOG_DBG << "=== Event DMCS_AT_END_READOUT received = ";
            Emitter msg; 
            msg << BeginMap; 
            msg << Key << "MSG_TYPE" << Value << "DMCS_AT_END_READOUT"; 
            msg << Key << "IMAGE_ID" << Value << SALInstance.imageName; 
            msg << Key << "IMAGE_INDEX" << Value << SALInstance.imageIndex; 
            msg << Key << "IMAGE_SEQUENCE_NAME" << Value << SALInstance.imageSequenceName; 
            msg << Key << "IMAGES_IN_SEQUENCE" << Value << SALInstance.imagesInSequence; 
            msg << EndMap; 
	    LOG_DBG << "Published msg is: " << msg.c_str(); 
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
    SAL_EFD mgr = SAL_EFD(); 
    EFD_logevent_largeFileObjectAvailableC SALInstance; 

    mgr.salEvent("EFD_logevent_largeFileObjectAvailable"); 
    SimplePublisher *publisher = new SimplePublisher(broker_addr); 

    while(1) { 
        status = mgr.getEvent_largeFileObjectAvailable(&SALInstance); 

        if (status == SAL__OK) { 
            string device = SALInstance.generator; 
            string msg_type; 
            if (device == "ATHeaderService") { 
                LOG_DBG << "=== Event AuxTel HeaderService received = ";
                msg_type = "DMCS_AT_HEADER_READY"; 
            } 
            else { 
                LOG_DBG << "=== Event Regular HeaderService received = ";
                msg_type = "DMCS_HEADER_READY"; 
            } 

            Emitter msg;
            msg << BeginMap; 
            msg << Key << "MSG_TYPE" << Value << msg_type; 
            msg << Key << "FILENAME" << Value << SALInstance.url; 
            msg << Key << "IMAGE_ID" << Value << SALInstance.id; 
            msg << EndMap; 	

	    LOG_DBG << "Published msg is: " << msg.c_str(); 
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
