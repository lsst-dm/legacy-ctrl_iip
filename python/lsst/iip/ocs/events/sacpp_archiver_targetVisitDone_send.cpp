

/*
 * This file contains the implementation for the archiver_targetVisitDone send test.
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
  archiver_logevent_targetVisitDoneC myData;
  if (argc < 2) {
     printf("Usage :  input parameters...\n");

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
  mgr.salEvent("archiver_logevent_targetVisitDone");

    sscanf(argv[1], "%d", &myData.priority);

  // generate event
  priority = myData.priority;
  mgr.logEvent_targetVisitDone(&myData, priority);
  cout << "=== Event targetVisitDone generated = " << endl;
  sleep(1);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return 0;
}


