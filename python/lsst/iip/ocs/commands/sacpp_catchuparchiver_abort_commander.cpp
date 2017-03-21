

/*
 * This file contains the implementation for the catchuparchiver_abort commander test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include "SAL_catchuparchiver.h"
#include "ccpp_sal_catchuparchiver.h"
#include "os.h"
#include <stdlib.h>
using namespace DDS;
using namespace catchuparchiver;

int main (int argc, char *argv[])
{ 
  int cmdId;
  int timeout=10;
  int status=0;

  catchuparchiver_command_abortC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  boolean	state;\n");
     exit(1);
  }
  SAL_catchuparchiver mgr = SAL_catchuparchiver();

  mgr.salCommand("catchuparchiver_command_abort");

  myData.device   = "all";
  myData.property = "abort";
  myData.action   = "";
    sscanf(argv[1], "%d", &myData.state);

  // generate command
  cmdId = mgr.issueCommand_abort(&myData);
  cout << "=== command abort issued = " << endl;
  status = mgr.waitForCompletion_abort(cmdId, timeout);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return status;
}


