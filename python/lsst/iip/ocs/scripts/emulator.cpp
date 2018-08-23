#include <iostream> 
#include "SAL_atArchiver.h"
#include "SAL_atcamera.h"
#include "SAL_efd.h"
#include "SAL_atHeaderService.h"
#include "ccpp_sal_atArchiver.h"
#include "ccpp_sal_atcamera.h"
#include "ccpp_sal_efd.h"
#include "ccpp_sal_atHeaderService.h"
#include "os.h"
#include "time.h" 
#include <typeinfo>
#include <map>

using namespace DDS;
using namespace atArchiver;
using namespace atcamera;
using namespace atHeaderService; 
using namespace efd;
using namespace std; 

#define TIMEOUT 10

template <typename T, typename U> 
using issueCommand = int (T::*)(U*); 

template <typename T> 
using waitForCompletion = salReturn (T::*)(int, unsigned int); 

string get_device(string name) { 
    string device; 
    if (name == "AR") device = "archiver"; 
    else if (name == "CU") device = "catchuparchiver"; 
    else if (name == "PP") device = "processingcluster"; 
    else if (name == "AT") device = "atArchiver"; 
    return device; 
} 

template <typename SAL_device, typename SAL_struct> 
void sendCommand(SAL_device mgr, string device, string command_name, issueCommand<SAL_device, SAL_struct> issueCommand, waitForCompletion<SAL_device> waitForCompletion){ 
    int cmdId;
    int timeout=TIMEOUT;
    int status=0;

    SAL_struct myData;
    string processor = get_device(device) + "_command_" + command_name; 
    mgr.salCommand(const_cast<char *>(processor.c_str()));

    myData.device   = device;
    myData.property = "none";
    myData.action   = "";
    myData.state = 1; 
    cmdId = (mgr.*issueCommand)(&myData);
    cout << "=== command enable issued = " << endl;
    status = (mgr.*waitForCompletion)(cmdId, timeout);
} 

template <typename SAL_device, typename SAL_struct> 
void sendCommand_start(SAL_device mgr, string device, string command_name, string config, issueCommand<SAL_device, SAL_struct> issueCommand, waitForCompletion<SAL_device> waitForCompletion){ 
    int cmdId;
    int timeout=TIMEOUT;
    int status=0;

    SAL_struct myData;
    string processor = get_device(device) + "_command_" + command_name; 
    mgr.salCommand(const_cast<char *>(processor.c_str()));

    myData.device   = device;
    myData.property = "none";
    myData.action   = "";
    myData.configuration = "Normal"; 
    cmdId = (mgr.*issueCommand)(&myData);
    cout << "=== command enable issued = " << endl;
    status = (mgr.*waitForCompletion)(cmdId, timeout);
} 

void process_command(string device, string command) { 
    SAL_atArchiver at = SAL_atArchiver(); 
    if (command == "startup") { 
	// enterControl
        issueCommand<SAL_atArchiver, atArchiver_command_enterControlC> iss2 = &SAL_atArchiver::issueCommand_enterControl; 
        waitForCompletion<SAL_atArchiver> wfc2 = &SAL_atArchiver::waitForCompletion_enterControl;
        sendCommand(at, device, command, iss2, wfc2); 

	// start
        issueCommand<SAL_atArchiver, atArchiver_command_startC> iss6 = &SAL_atArchiver::issueCommand_start; 
        waitForCompletion<SAL_atArchiver> wfc6 = &SAL_atArchiver::waitForCompletion_start;
        sendCommand_start(at, device, "Normal", command, iss6, wfc6); 

	// enable
        issueCommand<SAL_atArchiver, atArchiver_command_enableC> iss = &SAL_atArchiver::issueCommand_enable; 
        waitForCompletion<SAL_atArchiver> wfc = &SAL_atArchiver::waitForCompletion_enable;
        sendCommand(at, device, command, iss, wfc); 
    } 
    else if (command == "all") { 
	// enterControl
        issueCommand<SAL_atArchiver, atArchiver_command_enterControlC> iss2 = &SAL_atArchiver::issueCommand_enterControl; 
        waitForCompletion<SAL_atArchiver> wfc2 = &SAL_atArchiver::waitForCompletion_enterControl;
        sendCommand(at, device, command, iss2, wfc2); 

	// start
        issueCommand<SAL_atArchiver, atArchiver_command_startC> iss6 = &SAL_atArchiver::issueCommand_start; 
        waitForCompletion<SAL_atArchiver> wfc6 = &SAL_atArchiver::waitForCompletion_start;
        sendCommand_start(at, device, "Normal", command, iss6, wfc6); 

	// enable
        issueCommand<SAL_atArchiver, atArchiver_command_enableC> iss = &SAL_atArchiver::issueCommand_enable; 
        waitForCompletion<SAL_atArchiver> wfc = &SAL_atArchiver::waitForCompletion_enable;
        sendCommand(at, device, command, iss, wfc); 

	// disable
        issueCommand<SAL_atArchiver, atArchiver_command_disableC> iss1 = &SAL_atArchiver::issueCommand_disable; 
        waitForCompletion<SAL_atArchiver> wfc1 = &SAL_atArchiver::waitForCompletion_disable;
        sendCommand(at, device, command, iss1, wfc1); 

	// standby
        issueCommand<SAL_atArchiver, atArchiver_command_standbyC> iss4 = &SAL_atArchiver::issueCommand_standby; 
        waitForCompletion<SAL_atArchiver> wfc4 = &SAL_atArchiver::waitForCompletion_standby;
        sendCommand(at, device, command, iss4, wfc4); 

	// exitControl
        issueCommand<SAL_atArchiver, atArchiver_command_exitControlC> iss3 = &SAL_atArchiver::issueCommand_exitControl; 
        waitForCompletion<SAL_atArchiver> wfc3 = &SAL_atArchiver::waitForCompletion_exitControl;
        sendCommand(at, device, command, iss3, wfc3); 

	// abort
        issueCommand<SAL_atArchiver, atArchiver_command_abortC> iss5 = &SAL_atArchiver::issueCommand_abort; 
        waitForCompletion<SAL_atArchiver> wfc5 = &SAL_atArchiver::waitForCompletion_abort;
        sendCommand(at, device, command, iss5, wfc5); 
    } 
    else if (command == "shutdown") { 
	// disable
        issueCommand<SAL_atArchiver, atArchiver_command_disableC> iss1 = &SAL_atArchiver::issueCommand_disable; 
        waitForCompletion<SAL_atArchiver> wfc1 = &SAL_atArchiver::waitForCompletion_disable;
        sendCommand(at, device, command, iss1, wfc1); 

	// standby
        issueCommand<SAL_atArchiver, atArchiver_command_standbyC> iss4 = &SAL_atArchiver::issueCommand_standby; 
        waitForCompletion<SAL_atArchiver> wfc4 = &SAL_atArchiver::waitForCompletion_standby;
        sendCommand(at, device, command, iss4, wfc4); 

	// exitControl
        issueCommand<SAL_atArchiver, atArchiver_command_exitControlC> iss3 = &SAL_atArchiver::issueCommand_exitControl; 
        waitForCompletion<SAL_atArchiver> wfc3 = &SAL_atArchiver::waitForCompletion_exitControl;
        sendCommand(at, device, command, iss3, wfc3); 

    } 
    else if (command == "start") { 
        issueCommand<SAL_atArchiver, atArchiver_command_startC> iss6 = &SAL_atArchiver::issueCommand_start; 
        waitForCompletion<SAL_atArchiver> wfc6 = &SAL_atArchiver::waitForCompletion_start;
        sendCommand_start(at, device, "Normal", command, iss6, wfc6); 
    } 
    else if (command == "enable") { 
        issueCommand<SAL_atArchiver, atArchiver_command_enableC> iss = &SAL_atArchiver::issueCommand_enable; 
        waitForCompletion<SAL_atArchiver> wfc = &SAL_atArchiver::waitForCompletion_enable;
        sendCommand(at, device, command, iss, wfc); 
    }   
    else if (command == "disable") { 
        issueCommand<SAL_atArchiver, atArchiver_command_disableC> iss = &SAL_atArchiver::issueCommand_disable; 
        waitForCompletion<SAL_atArchiver> wfc = &SAL_atArchiver::waitForCompletion_disable;
        sendCommand(at, device, command, iss, wfc); 
    }   
    else if (command == "enterControl") { 
        issueCommand<SAL_atArchiver, atArchiver_command_enterControlC> iss = &SAL_atArchiver::issueCommand_enterControl; 
        waitForCompletion<SAL_atArchiver> wfc = &SAL_atArchiver::waitForCompletion_enterControl;
        sendCommand(at, device, command, iss, wfc); 
    }   
    else if (command == "exitControl") { 
        issueCommand<SAL_atArchiver, atArchiver_command_exitControlC> iss = &SAL_atArchiver::issueCommand_exitControl; 
        waitForCompletion<SAL_atArchiver> wfc = &SAL_atArchiver::waitForCompletion_exitControl;
        sendCommand(at, device, command, iss, wfc); 
    }   
    else if (command == "standby") { 
        issueCommand<SAL_atArchiver, atArchiver_command_standbyC> iss = &SAL_atArchiver::issueCommand_standby; 
        waitForCompletion<SAL_atArchiver> wfc = &SAL_atArchiver::waitForCompletion_standby;
        sendCommand(at, device, command, iss, wfc); 
    }   
    else if (command == "abort") { 
        issueCommand<SAL_atArchiver, atArchiver_command_abortC> iss = &SAL_atArchiver::issueCommand_abort; 
        waitForCompletion<SAL_atArchiver> wfc = &SAL_atArchiver::waitForCompletion_abort;
        sendCommand(at, device, command, iss, wfc); 
    }   
    at.salShutdown(); 
} 

// ************************************************************************
// SAL EVENTS 
// ************************************************************************
void process_atcamera_event(string event, string imgSeqName, string imgName, long imagesInSeq, long imgIdx) { 
    SAL_atcamera atcamera = SAL_atcamera();
    if (event == "endReadout") { 
        atcamera_logevent_endReadoutC mydata; 
        mydata.imageSequenceName = imgSeqName; 
        mydata.imagesInSequence = imagesInSeq; 
        mydata.imageName = imgName; 
        mydata.imageIndex = imgIdx; 
        mydata.timeStamp = 0; 
        mydata.exposureTime = 0; 
        mydata.priority = 0;  

        atcamera.salEventPub("atcamera_logevent_endReadout"); 
        atcamera.logEvent_endReadout(&mydata, 0); 

    }
    else if (event == "startIntegration") { 
        atcamera_logevent_startIntegrationC mydata; 
        mydata.imageSequenceName = imgSeqName; 
        mydata.imagesInSequence = imagesInSeq; 
        mydata.imageName = imgName; 
        mydata.imageIndex = imgIdx; 
        mydata.timeStamp = 0; 
        mydata.exposureTime = 0; 
        mydata.priority = 0;  

        atcamera.salEventPub("atcamera_logevent_startIntegration"); 
        atcamera.logEvent_startIntegration(&mydata, 0); 
    }
    atcamera.salShutdown(); 
} 

void process_atHeader_event(string url, string id) { 
    SAL_atHeaderService mgr = SAL_atHeaderService(); 
    mgr.salEventPub("atHeaderService_logevent_largeFileObjectAvailable"); 
    atHeaderService_logevent_largeFileObjectAvailableC data; 
    data.url = url; 
    data.generator = "atHeaderService";
    data.version = 0;
    data.checkSum = "0"; 
    data.mimeType = "0"; 
    data.byteSize = 0;
    data.id = id; 
    data.priority = 0;
    mgr.logEvent_largeFileObjectAvailable(&data, 0); 
    mgr.salShutdown();
} 

void process_efd_event(string url, string id) { 
    SAL_efd mgr = SAL_efd(); 
    mgr.salEventPub("efd_logevent_largeFileObjectAvailable"); 
    efd_logevent_largeFileObjectAvailableC data; 
    data.url = url; 
    data.generator = "atHeaderService";
    data.version = 0;
    data.checkSum = "0"; 
    data.mimeType = "0"; 
    data.byteSize = 0;
    data.id = id; 
    data.priority = 0;
    mgr.logEvent_largeFileObjectAvailable(&data, 0); 
    mgr.salShutdown();
} 

int main(int argc, char *argv[]) { 
    if (argc < 3) { 
        cout << "INCORRECT USAGE" << endl;
        cout << "Usage: ./emulator <device> <command|event> <arguments>" << endl; 
        cout << "device: AT, AR, CU, PP, atHeader, EFD, atcamera" << endl; 
        cout << "command: start, stop, enterControl, exitControl, standby, enable, disable, abort, startup, shutdown" << endl;
	cout << "event: " << endl; 
	cout << "     ./emulator EFD http://xxx/IMG_1.header IMG_1 " << endl; 
	cout << "     ./emulator atHeader http://xxx/IMG_1.header IMG_1 " << endl; 
	cout << "     ./emulator atcamera startIntegration ImgSeqName imagesInSeq imgName imgIdx" << endl; 
	cout << "     ./emulator atcamera endReadout ImgSeqName imagesInSeq imgName imgIdx" << endl; 
    } 
    else { 
        string command(argv[2]); 
        string device(argv[1]); 
        if (device == "atHeader") { 
	    string url(argv[3]); 
	    string id(argv[4]); 
            process_atHeader_event(url, id); 
        } 
        else if (device == "EFD") { 
	    string url(argv[3]); 
	    string id(argv[4]); 
            process_efd_event(url, id); 
        } 
        else if (device == "atcamera") { 
	    string imgSeqName(argv[3]); 
	    string imagesInSeq(argv[4]); 
	    string imgName(argv[5]);
	    string imgIdx(argv[6]); 
            process_atcamera_event(command, imgSeqName, imgName, stol(imagesInSeq), stol(imgIdx)); 
        } 
        else { 
            process_command(device, command); 
        } 
    } 
    return 0;
} 
