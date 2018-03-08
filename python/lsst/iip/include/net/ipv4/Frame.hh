
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
 
#ifndef IPV4_FRAME
#define IPV4_FRAME

#include "net/ipv4/Address.hh"
#include "net/ipv4/Members.hh"
#include "net/link/Frame.hh"

namespace IPV4  {

class  Frame : public Link::Frame {
public:
  Frame(const Address* dst, const Address* src) : Link::Frame(dst->link(), src->link(), (uint16_t)Link::Frame::IPV4), ipv4(dst, src) {} 
public:
 ~Frame() {}
public:
  Members ipv4;
  };

}

#endif


