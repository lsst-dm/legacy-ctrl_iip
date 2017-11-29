

/*
 * This file contains the implementation for the archiver_endReadout send test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include <unistd.h>
#include "SAL_archiver.h"
#include "ccpp_sal_archiver.h"
#include "os.h"
#include <stdlib.h>

#include "example_main.h"

using namespace DDS;
using namespace archiver;


int main (int argc, char *argv[])
{ 
  int priority = SAL__EVENT_INFO;
  archiver_logevent_endReadoutC myData;
  if (argc < 3) {
     printf("Usage :  input parameters...\n");

     printf("  string<128>	ImageName;\n");
     printf("  long	priority;\n");
     exit(1);
  }

#ifdef SAL_SUBSYSTEM_ID_IS_KEYED
  int archiverID = 1;
  if (getenv("LSST_archiver_ID") != NULL) {
     sscanf(getenv("LSST_archiver_ID"),"%d",&archiverID);
  } 
  SAL_archiver mgr = SAL_archiver(archiverID);
#else
  SAL_archiver mgr = SAL_archiver();
#endif
  mgr.salEvent("archiver_logevent_endReadout");

    myData.ImageName=argv[1];
    sscanf(argv[2], "%d", &myData.priority);

  // generate event
  priority = myData.priority;
  mgr.logEvent_endReadout(&myData, priority);
  cout << "=== Event endReadout generated = " << endl;
  sleep(1);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return 0;
}


