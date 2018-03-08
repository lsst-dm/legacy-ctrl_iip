
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
 
#ifndef UDP_MEMBERS
#define UDP_MEMBERS

#include "net/Endian.hh"

namespace UDP  {

class __attribute__((__packed__)) Members {
public:
  Members(uint16_t dst, uint16_t src, uint16_t length) : _src(src), _dst(dst), _length(Net::Endian::wire((uint16_t)(length + sizeof(Members)))), _checksum(0) {} 
public:  
  Members(const Members& clone) {uint64_t* dst = (uint64_t*)this; uint64_t* src = (uint64_t*)&clone; dst[0] = src[0];}   
public:
 ~Members() {}
public:
  unsigned length() const {return Net::Endian::local(_length);} 
  unsigned src()    const {return Net::Endian::local(_src);}
  unsigned dst()    const {return Net::Endian::local(_dst);}
private:
  uint16_t _src;
  uint16_t _dst;
  uint16_t _length;
  uint16_t _checksum;
  };
 
}

#endif


