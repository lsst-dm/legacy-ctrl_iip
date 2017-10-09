

/*
 * This file contains the implementation for the camera_endShutterOpen receive test.
 *
 ***/

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

/* entry point exported and demangled so symbol can be found in shared library */
extern "C"
{
  OS_API_EXPORT
  int test_camera_endShutterOpen_Log();
}

int test_camera_endShutterOpen_Log()
{ 
  os_time delay_10ms = { 0, 10000000 };
  int status = -1;

  camera_logevent_endShutterOpenC SALInstance;
#ifdef SAL_SUBSYSTEM_ID_IS_KEYED
  int cameraID = 1;
  if (getenv("LSST_camera_ID") != NULL) {
     sscanf(getenv("LSST_camera_ID"),"%d",&cameraID);
  } 
  SAL_camera mgr = SAL_camera(cameraID);
#else
  SAL_camera mgr = SAL_camera();
#endif
  mgr.salEvent("camera_logevent_endShutterOpen");
  cout << "=== Event endShutterOpen logger ready = " << endl;

  while (1) {
  // receive event
    status = mgr.getEvent_endShutterOpen(&SALInstance);
    if (status == SAL__OK) {
      cout << "=== Event endShutterOpen received = " << endl;

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
  return test_camera_endShutterOpen_Log();
}

