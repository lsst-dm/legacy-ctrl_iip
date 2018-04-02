

/*
 * This file contains the implementation for the efd_LargeFileObjectAvailable send test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include <unistd.h>
#include "SAL_efd.h"
#include "ccpp_sal_efd.h"
#include "os.h"
#include <stdlib.h>

#include "example_main.h"

using namespace DDS;
using namespace efd;


int main (int argc, char *argv[])
{ 
  int priority = SAL__EVENT_INFO;
  efd_logevent_LargeFileObjectAvailableC myData;
  if (argc < 9) {
     printf("Usage :  input parameters...\n");

     printf("  long	Byte_Size;\n");
     printf("  string	Checksum;\n");
     printf("  string	Generator;\n");
     printf("  string	Mime;\n");
     printf("  string	URL;\n");
     printf("  float	Version;\n");
     printf("  string<32>	ID;\n");
     printf("  long	priority;\n");
     exit(1);
  }

#ifdef SAL_SUBSYSTEM_ID_IS_KEYED
  int efdID = 1;
  if (getenv("LSST_efd_ID") != NULL) {
     sscanf(getenv("LSST_efd_ID"),"%d",&efdID);
  } 
  SAL_efd mgr = SAL_efd(efdID);
#else
  SAL_efd mgr = SAL_efd();
#endif
  mgr.salEvent("efd_logevent_LargeFileObjectAvailable");

    sscanf(argv[1], "%d", &myData.Byte_Size);
    myData.Checksum=argv[2];
    myData.Generator=argv[3];
    myData.Mime=argv[4];
    myData.URL=argv[5];
    sscanf(argv[6], "%f", &myData.Version);
    myData.ID=argv[7];
    sscanf(argv[8], "%d", &myData.priority);

  // generate event
  priority = myData.priority;
  mgr.logEvent_LargeFileObjectAvailable(&myData, priority);
  cout << "=== Event LargeFileObjectAvailable generated = " << endl;
  sleep(1);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return 0;
}


