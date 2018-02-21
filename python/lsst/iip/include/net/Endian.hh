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
**	000 - , 2007
**
**  Revision History:
**	None.
**
** --
*/
 
#ifndef NET_ENDIAN
#define NET_ENDIAN

#include <stdint.h>

namespace Net {

class Endian {
public:
  static uint64_t local(uint64_t net);
  static uint32_t local(uint32_t net);
  static int32_t  local(int32_t  net);
  static uint16_t local(uint16_t net);  
public:
  static uint64_t wire(uint64_t local);
  static uint32_t wire(uint32_t local);
  static int32_t  wire(int32_t  local);
  static uint16_t wire(uint16_t local);
public:   
  static uint32_t wire(const char* addr);
};
 
}

#endif
