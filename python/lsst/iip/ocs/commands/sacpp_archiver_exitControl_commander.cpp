

/*
 * This file contains the implementation for the archiver_exitControl commander test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include "SAL_archiver.h"
#include "ccpp_sal_archiver.h"
#include "os.h"
#include <stdlib.h>
using namespace DDS;
using namespace archiver;

int main (int argc, char *argv[])
{ 
  int cmdId;
  int timeout=10;
  int status=0;

  archiver_command_exitControlC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  boolean	state;\n");
     exit(1);
  }
  SAL_archiver mgr = SAL_archiver();

  mgr.salCommand("archiver_command_exitControl");

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


