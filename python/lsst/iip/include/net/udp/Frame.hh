
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
 
#ifndef UDP_FRAME
#define UDP_FRAME

#include "net/udp/Members.hh"
#include "net/ipv4/Frame.hh"
#include "net/link/Address.hh"
#include "net/ipv4/Address.hh"

namespace UDP  {

class __attribute__((__packed__)) Frame : public IPV4::Frame {
public: 
 Frame(uint16_t size, const IPV4::Address* dst, const IPV4::Address* src);
public:
 ~Frame() {} 
public:
  Members udp;
  };

/*
** ++
**
**
** --
*/

inline Frame::Frame(uint16_t size, const IPV4::Address* dst, const IPV4::Address* src) : 
 IPV4::Frame(dst, src), 
 udp(dst->port(), src->port(), size) 
 {
 }
 
}

#endif


