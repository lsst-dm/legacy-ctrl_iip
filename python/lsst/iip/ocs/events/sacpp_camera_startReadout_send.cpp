

/*
 * This file contains the implementation for the camera_startReadout send test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include <unistd.h>
#include "SAL_camera.h"
#include "ccpp_sal_camera.h"
#include "os.h"
#include <stdlib.h>

#include "example_main.h"

using namespace DDS;
using namespace camera;


int main (int argc, char *argv[])
{ 
  int priority = SAL__EVENT_INFO;
  camera_logevent_startReadoutC myData;
  if (argc < 2) {
     printf("Usage :  input parameters...\n");

     printf("  long	priority;\n");
     exit(1);
  }

#ifdef SAL_SUBSYSTEM_ID_IS_KEYED
  int cameraID = 1;
  if (getenv("LSST_camera_ID") != NULL) {
     sscanf(getenv("LSST_camera_ID"),"%d",&cameraID);
  } 
  SAL_camera mgr = SAL_camera(cameraID);
#else
  SAL_camera mgr = SAL_camera();
#endif
  mgr.salEvent("camera_logevent_startReadout");

    sscanf(argv[1], "%d", &myData.priority);

  // generate event
  priority = myData.priority;
  mgr.logEvent_startReadout(&myData, priority);
  cout << "=== Event startReadout generated = " << endl;
  sleep(1);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return 0;
}


