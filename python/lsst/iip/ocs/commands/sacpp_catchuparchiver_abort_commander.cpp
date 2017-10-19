

/*
 * This file contains the implementation for the catchuparchiver_abort commander test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include "SAL_catchuparchiver.h"
#include "ccpp_sal_catchuparchiver.h"
#include "os.h"
#include <stdlib.h>
#include "SimplePublisher.h" 
#include <yaml-cpp/yaml.h> 
using namespace YAML; 
using namespace DDS;
using namespace catchuparchiver;

int main (int argc, char *argv[])
{ 
  int cmdId;
  int timeout=20;
  int status=0;

  catchuparchiver_command_abortC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  boolean	state;\n");
     exit(1);
  }
  SAL_catchuparchiver mgr = SAL_catchuparchiver();

  Node n = LoadFile("../../tests/yaml/L1SystemCfg_Test_ocs_bridge.yaml");
  string broker = n["ROOT"]["BASE_BROKER_ADDR"].as<string>(); 
  ostringstream url; 
  url << "amqp://CL_16:CL_16@" << broker; 
  cout << url.str() << endl; 
  SimplePublisher *publisher = new SimplePublisher(url.str()); 


  mgr.salCommand("catchuparchiver_command_abort");

  myData.device   = "all";
  myData.property = "abort";
  myData.action   = "";
    sscanf(argv[1], "%d", &myData.state);

  // generate command
  cmdId = mgr.issueCommand_abort(&myData);
  cout << "=== command abort issued = " << endl;
  status = mgr.waitForCompletion_abort(cmdId, timeout);

  if (status == 303) { // completed_ok
     publisher->publish_message("test_dmcs_ocs_publish", "{ MSG_TYPE: ABORT_ACK, DEVICE: CU, CMD_ID: None, ACK_ID: None, ACK_BOOL: None, ACK_STATEMENT }");  
  } 

  /* Remove the DataWriters etc */
  mgr.salShutdown();
  if (status != SAL__CMD_COMPLETE) {
     exit(1);
  }
  exit(0);
}


