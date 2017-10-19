

/*
 * This file contains the implementation for the catchuparchiver_enable commander test.
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

  catchuparchiver_command_enableC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  boolean	state;\n");
     exit(1);
  }
  SAL_catchuparchiver mgr = SAL_catchuparchiver();

  Node n = LoadFile("../../tests/yaml/L1SystemCfg_Test_ocs_bridge.yaml");
  string broker = n["ROOT"]["BASE_BROKER_ADDR"].as<string>(); 
  ostringstream url; 
  url << "amqp://CL_11:CL_11@" << broker; 
  cout << url.str() << endl; 
  SimplePublisher *publisher = new SimplePublisher(url.str()); 


  mgr.salCommand("catchuparchiver_command_enable");

  myData.device   = "controller";
  myData.property = "command";
  myData.action   = "";
    sscanf(argv[1], "%d", &myData.state);

  // generate command
  cmdId = mgr.issueCommand_enable(&myData);
  cout << "=== command enable issued = " << endl;
  status = mgr.waitForCompletion_enable(cmdId, timeout);

  if (status == 303) { // completed_ok
     publisher->publish_message("test_dmcs_ocs_publish", "{ MSG_TYPE: ENABLE_ACK, DEVICE: CU, CMD_ID: None, ACK_ID: None, ACK_BOOL: None, ACK_STATEMENT }");  
  } 
  /* Remove the DataWriters etc */
  mgr.salShutdown();
  if (status != SAL__CMD_COMPLETE) {
     exit(1);
  }
  exit(0);
}


