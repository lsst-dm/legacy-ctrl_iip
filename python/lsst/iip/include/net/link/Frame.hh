
/*
**  Package:
**	
**
**  Abstract:
**      
**
** arm-rtems4.11-g++ -c net/src/ipv4/Socket.cc -Wno-psabi -fno-zero-initialized-in-bss -fPIC -march=armv7-a -mtune=cortex-a9 -mfpu=neon -mfloat-abi=softfp -DEXPORT=
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
 
#ifndef LINK_FRAME
#define LINK_FRAME

#include "net/link/Members.hh"
#include "net/link/Address.hh"

namespace Link {

class __attribute__((__packed__)) Frame  {
public:
  enum {ARP=0x806, IPV4=0x800}; 
public:
  Frame(const Address& src,                     uint16_t type=IPV4) : link(     src, type) {} 
  Frame(const Address& dst, const Address& src, uint16_t type=IPV4) : link(dst, src, type) {} 
  Frame(const Frame& clone)                                         : link(clone.link)     {} 
public:
 ~Frame() {}
private: 
  uint16_t _pad;
public:
  Members link; 
};

}

#endif



