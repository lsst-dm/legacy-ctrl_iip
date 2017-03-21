

/*
 * This file contains the implementation for the catchuparchiver_exitControl commander test.
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

  catchuparchiver_command_exitControlC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  boolean	state;\n");
     exit(1);
  }
  SAL_catchuparchiver mgr = SAL_catchuparchiver();

  mgr.salCommand("catchuparchiver_command_exitControl");

  myData.device   = "controller";
  myData.property = "command";
  myData.action   = "exit";
    sscanf(argv[1], "%d", &myData.state);

  // generate command
  cmdId = mgr.issueCommand_exitControl(&myData);
  cout << "=== command exitControl issued = " << endl;
  status = mgr.waitForCompletion_exitControl(cmdId, timeout);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return status;
}


