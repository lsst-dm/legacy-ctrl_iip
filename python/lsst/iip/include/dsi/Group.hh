/*
** ++
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
**	000 - January 09, 2007
**
**  Revision History:
**	None.
**
** --
*/
 
#ifndef DSI_GROUP
#define DSI_GROUP

#include "net/ipv4/Address.hh"

namespace DSI {

class __attribute__((__packed__)) Group : public IPV4::Address {
public:
  enum {MAX=63};  // Maximum number of services per partition
public:
  Group();
  Group(const IPV4::Address& address) : IPV4::Address(address) {}
  Group(unsigned service, unsigned partition=0);  
  Group(const Group& clone) : IPV4::Address(clone) {}
public:
 ~Group() {}
public: 
  Group& operator=(const Group& clone) { IPV4::Address::operator=(clone); return *this;}       
};

}

#endif
