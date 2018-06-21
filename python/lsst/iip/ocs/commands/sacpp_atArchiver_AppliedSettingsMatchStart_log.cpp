

/*
 * This file contains the implementation for the atArchiver_AppliedSettingsMatchStart receive test.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include "SAL_atArchiver.h"
#include "ccpp_sal_atArchiver.h"
#include "os.h"
#include <stdlib.h>

#include "example_main.h"
#include "SimplePublisher.h" 
#include <yaml-cpp/yaml.h> 
using namespace YAML; 

using namespace DDS;
using namespace atArchiver;

/* entry point exported and demangled so symbol can be found in shared library */
extern "C"
{
  OS_API_EXPORT
  int test_atArchiver_AppliedSettingsMatchStart_Log();
}

int test_atArchiver_AppliedSettingsMatchStart_Log()
{ 
  os_time delay_10ms = { 0, 10000000 };
  int status = -1;

  atArchiver_logevent_AppliedSettingsMatchStartC SALInstance;
#ifdef SAL_SUBSYSTEM_ID_IS_KEYED
  int atArchiverID = 1;
  if (getenv("LSST_atArchiver_ID") != NULL) {
     sscanf(getenv("LSST_atArchiver_ID"),"%d",&atArchiverID);
  } 
  SAL_atArchiver mgr = SAL_atArchiver(atArchiverID);
#else
  SAL_atArchiver mgr = SAL_atArchiver();
#endif
  mgr.salEvent("atArchiver_logevent_AppliedSettingsMatchStart");
  Node n = LoadFile("../../tests/yaml/L1SystemCfg_Test_ocs_bridge.yaml");
  string broker = n["ROOT"]["BASE_BROKER_ADDR"].as<string>(); 
  ostringstream url; 
  url << "amqp://EVN_7:EVN_7@" << broker; 
  cout << url.str() << endl; 
  SimplePublisher *publisher = new SimplePublisher(url.str()); 
  cout << "=== Event AppliedSettingsMatchStart logger ready = " << endl;

  while (1) {
  // receive event
    status = mgr.getEvent_AppliedSettingsMatchStart(&SALInstance);
    if (status == SAL__OK) {
      cout << "=== Event AppliedSettingsMatchStart received = " << endl;

    cout << "    appliedSettingsMatchStartIsTrue : " << SALInstance.appliedSettingsMatchStartIsTrue << endl;
    cout << "    priority : " << SALInstance.priority << endl;
     publisher->publish_message("test_dmcs_ocs_publish", "{ MSG_TYPE: APPLIED_SETTINGS_MATCH_START_EVENT, DEVICE: AT, SETTING: None, APPLIED: None }");  

    }
    os_nanoSleep(delay_10ms);
  }

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return 0;
}

int OSPL_MAIN (int argc, char *argv[])
{
  return test_atArchiver_AppliedSettingsMatchStart_Log();
}

