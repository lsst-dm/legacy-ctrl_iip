#ifndef DAQ_LOCATIONSETCLI
#define DAQ_LOCATIONSETCLI

#include "daq/LocationSet.hh"

namespace DAQ {

class LocationSetCli {
public:
  static void        usage(int indent=0);
  static LocationSet get(int nargs, char** args);
};
}


#endif
