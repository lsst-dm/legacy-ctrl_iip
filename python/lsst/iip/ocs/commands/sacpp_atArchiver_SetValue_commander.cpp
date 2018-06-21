

/*
 * This file contains the implementation for the atArchiver_SetValue commander test.
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

  atArchiver_command_SetValueC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  string	json_parameters;\n");
     exit(1);
  }
  SAL_atArchiver mgr = SAL_atArchiver();

  mgr.salCommand("atArchiver_command_SetValue");

  myData.device   = "controller";
  myData.property = "configuration";
  myData.action   = "set";
    myData.json_parameters=argv[1];

  // generate command
  cmdId = mgr.issueCommand_SetValue(&myData);
  cout << "=== command SetValue issued = " << endl;
  status = mgr.waitForCompletion_SetValue(cmdId, timeout);

  /* Remove the DataWriters etc */
  mgr.salShutdown();
  if (status != SAL__CMD_COMPLETE) {
     exit(1);
  }
  exit(0);
}


