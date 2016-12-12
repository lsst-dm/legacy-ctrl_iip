

/*
 * This file contains the implementation for the dm_abort commander test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include "SAL_dm.h"
#include "ccpp_sal_dm.h"
#include "os.h"
#include <stdlib.h>
using namespace DDS;
using namespace dm;

int main (int argc, char *argv[])
{ 
  int cmdId;
  int timeout=10;
  int status=0;

  dm_command_abortC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  string	state;\n");
     exit(1);
  }
  SAL_dm mgr = SAL_dm();

  mgr.salCommand("dm_command_abort");

  myData.device   = argv[1];
  myData.property = "abort";
  myData.action   = "";
    myData.state="";

  // generate command
  cmdId = mgr.issueCommand_abort(&myData);
  cout << "=== command abort issued = " << endl;
  status = mgr.waitForCompletion_abort(cmdId, timeout);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return status;
}


