
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
 
#ifndef RCE_FRAME
#define RCE_FRAME

#include <stdint.h>

namespace RCE {

class __attribute__((__packed__)) Frame {
public:
  Frame() {}                                                  
public:
 ~Frame() {}
public:
  void*    _payload;
  uint32_t _size;
  uint32_t _mid;
  void*    _frame; 
  };

}

#endif



