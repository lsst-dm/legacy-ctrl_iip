

/*
 * This file contains the implementation for the processingcluster_enterControl commander test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include "SAL_processingcluster.h"
#include "ccpp_sal_processingcluster.h"
#include "os.h"
#include <stdlib.h>
#include "SimplePublisher.h" 
#include <yaml-cpp/yaml.h> 
using namespace YAML; 
using namespace DDS;
using namespace processingcluster;

int main (int argc, char *argv[])
{ 
  int cmdId;
  int timeout=20;
  int status=0;

  processingcluster_command_enterControlC myData;
  if (argc < 2 ) {
     printf("Usage :  input parameters...\n");
     printf("  boolean	state;\n");
     exit(1);
  }
  SAL_processingcluster mgr = SAL_processingcluster();

  Node n = LoadFile("../../tests/yaml/L1SystemCfg_Test_ocs_bridge.yaml");
  string broker = n["ROOT"]["BASE_BROKER_ADDR"].as<string>(); 
  ostringstream url; 
  url << "amqp://CL_22:CL_22@" << broker; 
  cout << url.str() << endl; 
  SimplePublisher *publisher = new SimplePublisher(url.str()); 


  mgr.salCommand("processingcluster_command_enterControl");

  myData.device   = "controller";
  myData.property = "command";
  myData.action   = "allow";
    sscanf(argv[1], "%d", &myData.state);

  // generate command
  cmdId = mgr.issueCommand_enterControl(&myData);
  cout << "=== command enterControl issued = " << endl;
  status = mgr.waitForCompletion_enterControl(cmdId, timeout);


  if (status == 303) { // completed_ok
     publisher->publish_message("test_dmcs_ocs_publish", "{ MSG_TYPE: ENTER_CONTROL_ACK, DEVICE: PP, CMD_ID: None, ACK_ID: None, ACK_BOOL: None, ACK_STATEMENT }");  
  } 
  /* Remove the DataWriters etc */
  mgr.salShutdown();
  if (status != SAL__CMD_COMPLETE) {
     exit(1);
  }
  exit(0);
}


