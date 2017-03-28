

/*
 * This file contains the implementation for the processingcluster_exitControl commander test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include "SAL_processingcluster.h"
#include "ccpp_sal_processingcluster.h"
#include "os.h"
#include <stdlib.h>
using namespace DDS;
using namespace processingcluster;

int main (int argc, char *argv[])
{ 
  int cmdId;
  int timeout=10;
  int status=0;

  processingcluster_command_exitControlC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  boolean	state;\n");
     exit(1);
  }
  SAL_processingcluster mgr = SAL_processingcluster();

  mgr.salCommand("processingcluster_command_exitControl");

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


