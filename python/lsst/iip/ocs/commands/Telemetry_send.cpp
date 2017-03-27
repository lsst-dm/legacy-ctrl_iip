
/*
 * This file contains the implementation for the 'archiver_Event' executable.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include <unistd.h>
#include "SAL_archiver.h"
#include "ccpp_sal_archiver.h"
#include "os.h"


using namespace DDS;
using namespace archiver;

/* entry point exported and demangled so symbol can be found in shared library */
extern "C"
{
  OS_API_EXPORT
  int archiver_Event(char *alias , char *message);
}

int archiver_Event(char *alias, char *message)
{
  
  int priority = SAL__EVENT_INFO;

#ifdef SAL_SUBSYSTEM_ID_IS_KEYED
  int archiverID = 1;
  SAL_archiver mgr = SAL_archiver(archiverID);
#else
  SAL_archiver mgr = SAL_archiver();
#endif

  // generate event
  mgr.logEvent(message, priority);
  cout << "=== Telemetry " << alias << " generated = " << message << endl;
  sleep(1);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return 0;
}


int main (int argc, char *argv[])
{
  if (argc < 2) {
     cout << "A alias + message text is required at a minimum" << endl;
     exit(1);
  }

  ostringstream message; 
  message << "{" << argv[1] << "}"; 
  return archiver_Event ("None", const_cast<char *>(message.str().c_str()));
}


