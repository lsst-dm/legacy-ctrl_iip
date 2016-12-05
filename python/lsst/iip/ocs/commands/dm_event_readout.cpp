
/*
 * This file contains the implementation for the 'dm_Event' executable.
 *
 ***/

#include <string>
#include <sstream>
#include <iostream>
#include <unistd.h>
#include "SAL_dm.h"
#include "ccpp_sal_dm.h"
#include "os.h"

#include "example_main.h"

using namespace DDS;
using namespace dm;
using namespace std;


/* entry point exported and demangled so symbol can be found in shared library */
extern "C"
{
  OS_API_EXPORT
  int dm_Event(char *alias , char *message);
}

int dm_Event(char *alias, char *message)
{
  
  int priority = SAL__EVENT_INFO;

#ifdef SAL_SUBSYSTEM_ID_IS_KEYED
  int dmID = 1;
  SAL_dm mgr = SAL_dm(dmID);
#else
  SAL_dm mgr = SAL_dm();
#endif

  // generate event
  mgr.logEvent(message, priority);
  cout << "=== Event " << alias << " generated = " << message << endl;
  sleep(1);

  /* Remove the DataWriters etc */
  mgr.salShutdown();

  return 0;
}


int OSPL_MAIN (int argc, char *argv[])
{
  if (argc < 3) {
     cout << "A alias + message text is required at a minimum" << endl;
     exit(1);
  }
  
  // arg2 must be image_id
  ostringstream message; 
  message << "{MSG_TYPE: READOUT, IMAGE_ID: " << argv[2] << "}"; 
  return dm_Event (argv[1], const_cast<char *>(message.str().c_str()));
}


