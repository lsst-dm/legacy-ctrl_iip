
/*
**  Package:
**	
**
**  Abstract:
**      
**
**  Author:
**      Michael Huffer, SLAC (mehsys@slac.stanford.edu)
**
**  Creation Date:
**	    000 - April 06, 2011
**
**  Revision History:
**	    None.
**
** --
*/
 
#ifndef HKS_PARTITION
#define HKS_PARTITION

#include "dsi/Client.hh"

namespace HKS {

class Partition : public  DSI::Client {
public:
  enum Constant {RELEASE=0, MOUNTPOINT=1, ROLE=2, SOURCE=3, NONE=4};
public:
  Partition(const char* partition);
public:
 virtual ~Partition() {}
public:
  void reboot();
private:
  friend class Lookup;  
  };

}

#endif

