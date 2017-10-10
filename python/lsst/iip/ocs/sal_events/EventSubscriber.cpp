#include <string>
#include <sstream>
#include <iostream>
#include "SAL_camera.h"
#include "ccpp_sal_camera.h"
#include "os.h"
#include <stdlib.h>

#include "example_main.h"

using namespace DDS;
using namespace camera;

// TODO: put everything in the 


EventSubscriber::EventSubscriber() { 

}

EventSubscriber::~EventSubscriber() { 

} 



extern "C"
{
  OS_API_EXPORT
  int test_camera_endShutterClose_Log();
}

int test_camera_endShutterClose_Log()
{ 
  os_time delay_10ms = { 0, 10000000 };
  int status = -1;

  camera_logevent_endShutterCloseC SALInstance;
#ifdef SAL_SUBSYSTEM_ID_IS_KEYED
  int cameraID = 1;
  if (getenv("LSST_camera_ID") != NULL) {
     sscanf(getenv("LSST_camera_ID"),"%d",&cameraID);
  } 
  SAL_camera mgr = SAL_camera(cameraID);
#else
  SAL_camera mgr = SAL_camera();
#endif
  mgr.salEvent("camera_logevent_endShutterClose");
  cout << "=== Event endShutterClose logger ready = " << endl;

  while (1) {
  // receive event
    status = mgr.getEvent_endShutterClose(&SALInstance);
    if (status == SAL__OK) {
      cout << "=== Event endShutterClose received = " << endl;

    cout << "    priority : " << SALInstance.priority << endl;

    }
    os_nanoSleep(delay_10ms);
  }

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return 0;
}

int OSPL_MAIN (int argc, char *argv[])
{
  return test_camera_endShutterClose_Log();
}

