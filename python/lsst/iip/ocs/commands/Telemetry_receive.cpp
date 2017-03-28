
/*
 * This file contains the implementation for the 'archiver_EventLogger' executable.
 *
 ***/


#include <string>
#include <sstream>
#include <iostream>
#include "SAL_archiver.h"
#include "ccpp_sal_archiver.h"
#include "os.h"


using namespace DDS;
using namespace archiver;

/* entry point exported and demangled so symbol can be found in shared library */
extern "C"
{
  OS_API_EXPORT
  int archiver_EventLogger(char *topic_name);
}


int archiver_EventLogger(char *topic_name)
{
  os_time delay_2ms = { 0, 2000000 };
  os_time delay_200ms = { 0, 200000000 };
  archiver_logeventC SALInstance;


#ifdef SAL_SUBSYSTEM_ID_IS_KEYED
  int archiverID = 1;
  SAL_archiver mgr = SAL_archiver(archiverID);
#else
  SAL_archiver mgr = SAL_archiver();
#endif


  cout << "=== [Telemetry Receiver] Ready ..." << endl;

  bool closed = false;
  ReturnCode_t status =  - 1;
  int count = 0;
  while (!closed && count < 1500) // We dont want the example to run indefinitely
  {
    status = mgr.getEventC(&SALInstance);
    if (status == SAL__OK) {
        cout << "=== message = " + SALInstance.message << endl;
    }
    os_nanoSleep(delay_200ms);
    ++count;
  }

  os_nanoSleep(delay_2ms);

  //cleanup
  mgr.salShutdown();

  return 0;
}

int main (int argc, char *argv[])
{
  return archiver_EventLogger("archiver_logevent");
}


