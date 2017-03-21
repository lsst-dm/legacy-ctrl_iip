

/*
 * This file contains the implementation for the archiver_start commander test.
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

  archiver_command_startC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  string	configuration;\n");
     exit(1);
  }
  SAL_archiver mgr = SAL_archiver();

  mgr.salCommand("archiver_command_start");

  myData.device   = "configuration";
  myData.property = "set";
  myData.action   = "apply";
    myData.configuration=argv[1];

  // generate command
  cmdId = mgr.issueCommand_start(&myData);
  cout << "=== command start issued = " << endl;
  status = mgr.waitForCompletion_start(cmdId, timeout);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return status;
}


