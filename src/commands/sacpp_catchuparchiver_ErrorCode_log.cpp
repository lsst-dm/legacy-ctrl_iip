

/*
 * This file contains the implementation for the catchuparchiver_ErrorCode receive test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include "SAL_catchuparchiver.h"
#include "ccpp_sal_catchuparchiver.h"
#include "os.h"
#include <stdlib.h>

#include "example_main.h"
#include "SimplePublisher.h" 
#include <yaml-cpp/yaml.h> 
using namespace YAML; 

using namespace DDS;
using namespace catchuparchiver;

/* entry point exported and demangled so symbol can be found in shared library */
extern "C"
{
  OS_API_EXPORT
  int test_catchuparchiver_ErrorCode_Log();
}

int test_catchuparchiver_ErrorCode_Log()
{ 
  os_time delay_10ms = { 0, 10000000 };
  int status = -1;

  catchuparchiver_logevent_ErrorCodeC SALInstance;
#ifdef SAL_SUBSYSTEM_ID_IS_KEYED
  int catchuparchiverID = 1;
  if (getenv("LSST_catchuparchiver_ID") != NULL) {
     sscanf(getenv("LSST_catchuparchiver_ID"),"%d",&catchuparchiverID);
  } 
  SAL_catchuparchiver mgr = SAL_catchuparchiver(catchuparchiverID);
#else
  SAL_catchuparchiver mgr = SAL_catchuparchiver();
#endif
  mgr.salEvent("catchuparchiver_logevent_ErrorCode");
  Node n = LoadFile("../../tests/yaml/L1SystemCfg_Test_ocs_bridge.yaml");
  string broker = n["ROOT"]["BASE_BROKER_ADDR"].as<string>(); 
  ostringstream url; 
  url << "amqp://EVN_11:EVN_11@" << broker; 
  cout << url.str() << endl; 
  SimplePublisher *publisher = new SimplePublisher(url.str()); 
  cout << "=== Event ErrorCode logger ready = " << endl;

  while (1) {
  // receive event
    status = mgr.getEvent_ErrorCode(&SALInstance);
    if (status == SAL__OK) {
      cout << "=== Event ErrorCode received = " << endl;

    cout << "    errorCode : " << SALInstance.errorCode << endl;
    cout << "    priority : " << SALInstance.priority << endl;

     publisher->publish_message("test_dmcs_ocs_publish", "{ MSG_TYPE: ERROR_CODE_EVENT, DEVICE: CU, ERROR_CODE: None }");  
    }
    os_nanoSleep(delay_10ms);
  }

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return 0;
}

int OSPL_MAIN (int argc, char *argv[])
{
  return test_catchuparchiver_ErrorCode_Log();
}

