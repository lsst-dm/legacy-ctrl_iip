

/*
 * This file contains the implementation for the atcamera_startIntegration send test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include <unistd.h>
#include "SAL_atcamera.h"
#include "ccpp_sal_atcamera.h"
#include "os.h"
#include <stdlib.h>

#include "example_main.h"

using namespace DDS;
using namespace atcamera;


int main (int argc, char *argv[])
{ 
  int priority = SAL__EVENT_INFO;
  atcamera_logevent_startIntegrationC myData;
  if (argc < 8) {
     printf("Usage :  input parameters...\n");

     printf("  string	imageSequenceName;\n");
     printf("  long	imagesInSequence;\n");
     printf("  string	imageName;\n");
     printf("  long	imageIndex;\n");
     printf("  double	timeStamp;\n");
     printf("  double	exposureTime;\n");
     printf("  long	priority;\n");
     exit(1);
  }

#ifdef SAL_SUBSYSTEM_ID_IS_KEYED
  int atcameraID = 1;
  if (getenv("LSST_atcamera_ID") != NULL) {
     sscanf(getenv("LSST_atcamera_ID"),"%d",&atcameraID);
  } 
  SAL_atcamera mgr = SAL_atcamera(atcameraID);
#else
  SAL_atcamera mgr = SAL_atcamera();
#endif
  mgr.salEvent("atcamera_logevent_startIntegration");

    myData.imageSequenceName=argv[1];
    sscanf(argv[2], "%d", &myData.imagesInSequence);
    myData.imageName=argv[3];
    sscanf(argv[4], "%d", &myData.imageIndex);
    sscanf(argv[5], "%lf", &myData.timeStamp);
    sscanf(argv[6], "%lf", &myData.exposureTime);
    sscanf(argv[7], "%d", &myData.priority);

  // generate event
  priority = myData.priority;
  mgr.logEvent_startIntegration(&myData, priority);
  cout << "=== Event startIntegration generated = " << endl;
  sleep(1);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return 0;
}


