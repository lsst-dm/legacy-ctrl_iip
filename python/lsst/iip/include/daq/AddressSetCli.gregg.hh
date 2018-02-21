#ifndef DAQ_ADDRESSSETCLI
#define DAQ_ADDRESSSETCLI

#include "daq/AddressSet.hh"

namespace DAQ {

class AddressSetCli {
public:
  static void usage(int indent=0);
  static AddressSet get(int argc, char** argv);
};
}


#endif
