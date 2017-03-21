

/*
 * This file contains the implementation for the processingcluster_enable commander test.
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

  processingcluster_command_enableC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  boolean	state;\n");
     exit(1);
  }
  SAL_processingcluster mgr = SAL_processingcluster();

  mgr.salCommand("processingcluster_command_enable");

  myData.device   = "controller";
  myData.property = "command";
  myData.action   = "";
    sscanf(argv[1], "%d", &myData.state);

  // generate command
  cmdId = mgr.issueCommand_enable(&myData);
  cout << "=== command enable issued = " << endl;
  status = mgr.waitForCompletion_enable(cmdId, timeout);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return status;
}


