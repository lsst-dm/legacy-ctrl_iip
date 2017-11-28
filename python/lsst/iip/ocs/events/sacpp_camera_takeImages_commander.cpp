

/*
 * This file contains the implementation for the camera_takeImages commander test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include "SAL_camera.h"
#include "ccpp_sal_camera.h"
#include "os.h"
#include <stdlib.h>
using namespace DDS;
using namespace camera;

int main (int argc, char *argv[])
{ 
  int cmdId;
  int timeout=10;
  int status=0;

  camera_command_takeImagesC myData;
  if (argc < 8 ) {
     printf("Usage :  input parameters...\n");
     printf("  long	numImages;\n");
     printf("  double	expTime;\n");
     printf("  boolean	shutter;\n");
     printf("  boolean	science;\n");
     printf("  boolean	guide;\n");
     printf("  boolean	wfs;\n");
     printf("  string	imageSequenceName;\n");
     exit(1);
  }
  SAL_camera mgr = SAL_camera();

  mgr.salCommand("camera_command_takeImages");

  myData.device   = "takeImages";
  myData.property = "";
  myData.action   = "";
    sscanf(argv[1], "%d", &myData.numImages);
    sscanf(argv[2], "%lf", &myData.expTime);
    sscanf(argv[3], "%d", &myData.shutter);
    sscanf(argv[4], "%d", &myData.science);
    sscanf(argv[5], "%d", &myData.guide);
    sscanf(argv[6], "%d", &myData.wfs);
    myData.imageSequenceName=argv[7];

  // generate command
  cmdId = mgr.issueCommand_takeImages(&myData);
  cout << "=== command takeImages issued = " << endl;
  status = mgr.waitForCompletion_takeImages(cmdId, timeout);

  /* Remove the DataWriters etc */
  mgr.salShutdown();
  if (status != SAL__CMD_COMPLETE) {
     exit(1);
  }
  exit(0);
}


