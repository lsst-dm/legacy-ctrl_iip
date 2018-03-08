
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
 
#ifndef LINK_MEMBERS
#define LINK_MEMBERS

#include "net/Endian.hh"
#include "net/link/Address.hh"

namespace Link {

class __attribute__((__packed__)) Members {
public:
  Members(                    const Address& src, uint16_t type);  
  Members(const Address& dst, const Address& src, uint16_t type);  
public:
 ~Members() {}
public: 
  const uint8_t* src()  const {return _src;}                    
  const uint8_t* dst()  const {return _dst;}                    
  unsigned       type() const {return Net::Endian::local(_type);}
private:
  uint8_t  _dst[6];
  uint8_t  _src[6];
  uint16_t _type; 
};

/*
** ++
**
**
** --
*/

inline Members::Members(const Address& src, uint16_t type)
 {
  
 _dst[0] = 0xFF;
 _dst[1] = 0xFF;
 _dst[2] = 0xFF;
 _dst[3] = 0xFF;
 _dst[4] = 0xFF;
 _dst[5] = 0xFF;
 
 src.set(_src);
      
 _type = Net::Endian::wire(type);
 
 }  

/*
** ++
**
**
** --
*/

inline Members::Members(const Address& dst, const Address& src, uint16_t type)
 {
 
 dst.set(_dst);
 src.set(_src);
 
 _type = Net::Endian::wire(type);
 
 }  

}

#endif



