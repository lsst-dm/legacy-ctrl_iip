
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
 
#ifndef SSU_SHUT
#define SSU_SHUT
 
#include "dsi/Call.hh" 
#include "dsi/Address.hh"

#include "ssu/Shelf.hh"

namespace SSU {

class Shut : public DSI::Call {
public:
  Shut(Shelf&);
  Shut(Shelf&, const DSI::Address*);
public:  
 ~Shut() {};
  }; 

}

#endif

