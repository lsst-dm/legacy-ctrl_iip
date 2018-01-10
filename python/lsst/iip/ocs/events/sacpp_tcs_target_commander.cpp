

/*
 * This file contains the implementation for the tcs_target commander test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include "SAL_tcs.h"
#include "ccpp_sal_tcs.h"
#include "os.h"
#include <stdlib.h>
using namespace DDS;
using namespace tcs;

int main (int argc, char *argv[])
{ 
  int cmdId;
  int timeout=10;
  int status=0;

  tcs_command_targetC myData;
  if (argc < 12 ) {
     printf("Usage :  input parameters...\n");
     printf("  long	targetId;\n");
     printf("  long	fieldId;\n");
     printf("  long	groupId;\n");
     printf("  string<64>	filter;\n");
     printf("  double	requestTime;\n");
     printf("  double	ra;\n");
     printf("  double	dec;\n");
     printf("  double	angle;\n");
     printf("  long	num_exposures;\n");
     printf("  long	exposure_times;\n");
     printf("  double	slew_time;\n");
     exit(1);
  }
  SAL_tcs mgr = SAL_tcs();

  mgr.salCommand("tcs_command_target");

  myData.device   = "";
  myData.property = "";
  myData.action   = "";
    sscanf(argv[1], "%d", &myData.targetId);
    sscanf(argv[2], "%d", &myData.fieldId);
    sscanf(argv[3], "%d", &myData.groupId);
    myData.filter=argv[4];
    sscanf(argv[5], "%lf", &myData.requestTime);
    sscanf(argv[6], "%lf", &myData.ra);
    sscanf(argv[7], "%lf", &myData.dec);
    sscanf(argv[8], "%lf", &myData.angle);
    sscanf(argv[9], "%d", &myData.num_exposures);
    sscanf(argv[10], "%d", &myData.exposure_times);
    sscanf(argv[11], "%lf", &myData.slew_time);

  // generate command
  cmdId = mgr.issueCommand_target(&myData);
  cout << "=== command target issued = " << endl;
  status = mgr.waitForCompletion_target(cmdId, timeout);

  /* Remove the DataWriters etc */
  mgr.salShutdown();
  if (status != SAL__CMD_COMPLETE) {
     exit(1);
  }
  exit(0);
}


