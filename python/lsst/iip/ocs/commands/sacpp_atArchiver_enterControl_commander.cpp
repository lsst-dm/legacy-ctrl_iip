

/*
 * This file contains the implementation for the atArchiver_enterControl commander test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include "SAL_atArchiver.h"
#include "ccpp_sal_atArchiver.h"
#include "os.h"
#include <stdlib.h>
using namespace DDS;
using namespace atArchiver;

int main (int argc, char *argv[])
{ 
  int cmdId;
  int timeout=10;
  int status=0;

  atArchiver_command_enterControlC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  boolean	state;\n");
     exit(1);
  }
  SAL_atArchiver mgr = SAL_atArchiver();

  mgr.salCommand("atArchiver_command_enterControl");

  myData.device   = "controller";
  myData.property = "command";
  myData.action   = "allow";
    sscanf(argv[1], "%d", &myData.state);

  // generate command
  cmdId = mgr.issueCommand_enterControl(&myData);
  cout << "=== command enterControl issued = " << endl;
  status = mgr.waitForCompletion_enterControl(cmdId, timeout);

  /* Remove the DataWriters etc */
  mgr.salShutdown();
  if (status != SAL__CMD_COMPLETE) {
     exit(1);
  }
  exit(0);
}


