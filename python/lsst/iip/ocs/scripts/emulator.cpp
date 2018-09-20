#include "SAL_impl.h"
#include <yaml-cpp/yaml.h>
#include "SAL_atcamera.h"
#include "ccpp_sal_atcamera.h"
#include "SAL_efd.h"
#include "ccpp_sal_efd.h"
#include <cstdlib>

using namespace YAML; 
using namespace atcamera;
using namespace efd;

using funcptr = void (*)(string, Node); 

void show_manual() { 
    cout << "INCORRECT USAGE" << endl;
    cout << "Usage: ./emulator <device> <command|event> <arguments>" << endl; 
    cout << "device: AT, AR, CU, PP, atHeader, EFD, atcamera" << endl; 
    cout << "command: start, stop, enterControl, exitControl, standby, enable, disable, abort, startup, shutdown" << endl;
    cout << "event: " << endl; 
    cout << "     ./emulator EFD atHeaderService http://xxx/IMG_1.header IMG_1 " << endl; 
    cout << "     ./emulator atHeader http://xxx/IMG_1.header IMG_1 " << endl; 
    cout << "     ./emulator atcamera startIntegration ImgSeqName imagesInSeq imgName imgIdx" << endl; 
    cout << "     ./emulator atcamera endReadout ImgSeqName imagesInSeq imgName imgIdx" << endl; 
} 

void send_command_at(string command, Node n) { 
    SAL<SAL_archiver, SAL_atArchiver> mgr;
    if (command == "all") { 
        mgr.send_command<atArchiver_command_enableC>("AT", "enable");
        mgr.send_command<atArchiver_command_disableC>("AT", "disable");
        mgr.send_command<atArchiver_command_enterControlC>("AT", "enterControl");
        mgr.send_command<atArchiver_command_exitControlC>("AT", "exitControl");
        atArchiver_command_startC atStart; 
        atStart.configuration = "Normal";
        mgr.send_command_start<atArchiver_command_startC>(atStart, "AT", "start");
        mgr.send_command<atArchiver_command_standbyC>("AT", "standby");
        mgr.send_command<atArchiver_command_abortC>("AT", "abort");
    } 
    else if (command == "enable") { 
        mgr.send_command<atArchiver_command_enableC>("AT", "enable");
    }
    else if (command == "disable") { 
        mgr.send_command<atArchiver_command_disableC>("AT", "disable");
    }
    else if (command == "enterControl") { 
        mgr.send_command<atArchiver_command_enterControlC>("AT", "enterControl");
    }
    else if (command == "exitControl") { 
        mgr.send_command<atArchiver_command_exitControlC>("AT", "exitControl");
    }
    else if (command == "start") { 
        atArchiver_command_startC atStart; 
        atStart.configuration = "Normal";
        mgr.send_command_start<atArchiver_command_startC>(atStart, "AT", "start");
    }
    else if (command == "standby") { 
        mgr.send_command<atArchiver_command_standbyC>("AT", "standby");
    }
    else if (command == "abort") { 
        mgr.send_command<atArchiver_command_abortC>("AT", "abort");
    }
    else if (command == "startup") { 
        mgr.send_command<atArchiver_command_enterControlC>("AT", "enterControl");
        atArchiver_command_startC atStart; 
        atStart.configuration = "Normal";
        mgr.send_command_start<atArchiver_command_startC>(atStart, "AT", "start");
        mgr.send_command<atArchiver_command_enableC>("AT", "enable");
    }
    else if (command == "shutdown") { 
        mgr.send_command<atArchiver_command_disableC>("AT", "disable");
        mgr.send_command<atArchiver_command_standbyC>("AT", "standby");
        mgr.send_command<atArchiver_command_exitControlC>("AT", "exitControl");
    }
    sleep(1); // very very important
    mgr.shut_down();
} 

void send_command_ar(string command, Node n) { } 
void send_command_cu(string command, Node n) { } 
void send_command_pp(string command, Node n) { } 

void send_event_efd(string event, Node n) {
    string url = n["URL"].as<string>();
    string img_idx = n["IMG_IDX"].as<string>();
    string generator = n["GENERATOR"].as<string>();
    efd_logevent_largeFileObjectAvailableC myData;

    SAL_efd mgr = SAL_efd();
    mgr.salEventPub("efd_logevent_largeFileObjectAvailable");

    myData.url = url;
    myData.generator = generator; 
    myData.version = 0;
    myData.checkSum = "";
    myData.mimeType = "";
    myData.byteSize = 0;
    myData.id = img_idx;
    myData.priority = 0;
    mgr.logEvent_largeFileObjectAvailable(&myData, 0);
    cout << "=== Event largeFileObjectAvailable generated = " << endl;
    sleep(1); // very very important
    mgr.salShutdown();
} 

void send_event_atcamera(string event, Node n) { 
    string img_seq = n["IMG_SEQ_NAME"].as<string>();              
    long imgs_in_seq = n["IMGS_IN_SEQ"].as<long>();
    string img_name = n["IMG_NAME"].as<string>();
    long img_idx = n["IMG_IDX"].as<long>();

    int priority = SAL__EVENT_INFO;
    SAL_atcamera mgr = SAL_atcamera();
    if (event == "startIntegration") { 
        atcamera_logevent_startIntegrationC myData;

        mgr.salEventPub("atcamera_logevent_startIntegration");
        myData.imageSequenceName = img_seq; 
        myData.imagesInSequence = imgs_in_seq;
        myData.imageName = img_name;
        myData.imageIndex = img_idx;
        myData.timeStamp = 0;
        myData.exposureTime = 0;
        myData.priority = 0;

        priority = myData.priority;
        mgr.logEvent_startIntegration(&myData, priority);
        cout << "=== Event startIntegration generated = " << endl;
    }
    else if (event == "endReadout") { 
        atcamera_logevent_endReadoutC myData;

        mgr.salEventPub("atcamera_logevent_endReadout");
        myData.imageSequenceName = img_seq; 
        myData.imagesInSequence = imgs_in_seq;
        myData.imageName = img_name;
        myData.imageIndex = img_idx;
        myData.timeStamp = 0;
        myData.exposureTime = 0;
        myData.priority = 0;

        priority = myData.priority;
        mgr.logEvent_endReadout(&myData, priority);
        cout << "=== Event endReadout generated = " << endl;
    }
    sleep(1); // very very important
    mgr.salShutdown();
} 

void send_event_camera(string event, Node n) { } 
void send_event_atHeader(string event, Node n) { } 

map<string, funcptr> device_map = { 
    { "AT", send_command_at }, 
    { "AR", send_command_ar },
    { "CU", send_command_cu }, 
    { "PP", send_command_pp }, 
    { "efd", send_event_efd }, 
    { "atcamera", send_event_atcamera }, 
    { "camera", send_event_camera },
    { "atHeader", send_event_atHeader },
};

int main(int argc, char *argv[]) { 
    if (argc < 3) { 
        show_manual();
    } 
    else { 
        string command(argv[2]); 
        string device(argv[1]); 
        funcptr send_func = device_map[device]; 
        Node n; 
        if (device == "atcamera") { 
            n["IMG_SEQ_NAME"] = argv[3];              
            n["IMGS_IN_SEQ"] = atoi(argv[4]);  
            n["IMG_NAME"] = argv[5];  
            n["IMG_IDX"] = atoi(argv[6]); 
        } 
        else if (device == "camera") {
            n["IMG_SEQ_NAME"] = argv[3];              
            n["IMGS_IN_SEQ"] = atol(argv[4]);  
            n["IMG_NAME"] = argv[5];  
            n["IMG_IDX"] = atol(argv[6]); 
        } 
        else if (device == "efd") {
            n["GENERATOR"] = command;
            n["URL"] = argv[3]; 
            n["IMG_IDX"] = argv[4];
        } 
        else if (device == "atHeader") {
            n["GENERATOR"] = command;
            n["URL"] = argv[3]; 
            n["IMG_IDX"] = argv[4];
        } 
        else { }

        (*send_func)(command, n); 
    }
    return 0;
} 
