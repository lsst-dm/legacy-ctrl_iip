

/*
 * This file contains the implementation for the dm_standby commander test.
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

  dm_command_standbyC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  string	state;\n");
     exit(1);
  }
  SAL_dm mgr = SAL_dm();

  mgr.salCommand("dm_command_standby");

  myData.device   = argv[1];
  myData.property = "command";
  myData.action   = "stop";
    myData.state="";

  // generate command
  cmdId = mgr.issueCommand_standby(&myData);
  cout << "=== command standby issued = " << endl;
  status = mgr.waitForCompletion_standby(cmdId, timeout);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return status;
}


