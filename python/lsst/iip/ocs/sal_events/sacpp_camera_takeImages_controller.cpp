

/*
 * This file contains the implementation for the camera_takeImages controller test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include "SAL_camera.h"
#include "ccpp_sal_camera.h"
#include "os.h"
#include <stdlib.h>
#include "SimplePublisher.h" 
using namespace DDS;
using namespace camera;

/* entry point exported and demangled so symbol can be found in shared library */
extern "C"
{
  OS_API_EXPORT
  int test_camera_takeImages_controller();
}

int test_camera_takeImages_controller()
{ 
  os_time delay_10ms = { 0, 10000000 };
  int cmdId = -1;
  int timeout = 1;
  camera_command_takeImagesC SALInstance;
  SAL_camera mgr = SAL_camera();

  mgr.salProcessor("camera_command_takeImages");
  SimplePublisher *publisher = new SimplePublisher("amqp://TakeImage:TakeImage@141.142.208.209:5672/%2fbunny");
  cout << "=== camera_takeImages controller ready " << endl;

  while (1) {
    // receive command
    cmdId = mgr.acceptCommand_takeImages(&SALInstance);
    if (cmdId > 0) {
       cout << "=== command takeImages received = " << endl;

        cout << "    device : " << SALInstance.device << endl;
        cout << "    property : " << SALInstance.property << endl;
        cout << "    action : " << SALInstance.action << endl;
        cout << "    value : " << SALInstance.value << endl;
        cout << "    numImages : " << SALInstance.numImages << endl;
        cout << "    expTime : " << SALInstance.expTime << endl;
        cout << "    shutter : " << SALInstance.shutter << endl;
        cout << "    science : " << SALInstance.science << endl;
        cout << "    guide : " << SALInstance.guide << endl;
        cout << "    wfs : " << SALInstance.wfs << endl;
        cout << "    imageSequenceName : " << SALInstance.imageSequenceName << endl;
       ostringstream msg;
       msg << "{ MSG_TYPE: TAKE_IMAGES"
           << ", DEVICE: " << SALInstance.device
           << ", PROPERTY: " << SALInstance.property
           << ", ACTION: " << SALInstance.action
           << ", VALUE: " << SALInstance.value
           << ", NUM_IMAGES: " << SALInstance.numImages
           << ", EXP_TIME: " << SALInstance.expTime
           << ", SHUTTER: " << SALInstance.shutter
           << ", SCIENCE: " << SALInstance.science
           << ", GUIDE: " << SALInstance.guide
           << ", WFS: " << SALInstance.wfs
           << ", IMAGE_SEQUENCENAME: " << SALInstance.imageSequenceName << "}"; 
       publisher->publish_message("ocs_dmcs_consume", msg.str());

       if (timeout > 0) {
          mgr.ackCommand_takeImages(cmdId, SAL__CMD_INPROGRESS, 0, "Ack : OK");
          os_nanoSleep(delay_10ms);
       }       
       mgr.ackCommand_takeImages(cmdId, SAL__CMD_COMPLETE, 0, "Done : OK");
    }
    os_nanoSleep(delay_10ms);
  }

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return 0;
}

int main (int argc, char *argv[])
{
  return test_camera_takeImages_controller();
}

