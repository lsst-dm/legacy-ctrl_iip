
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
 
#ifndef SSU_RESET
#define SSU_RESET

#include "dsi/Location.hh"
#include "dsi/Call.hh"
#include "dsi/Address.hh"

#include "ssu/Shelf.hh"

namespace SSU {

class Reset  : public DSI::Call {
public:
  Reset(Shelf&);
  Reset(Shelf&, const DSI::Address*);
public: 
  bool wait(DSI::Location&, int& error);
public:
 ~Reset() {} 
 };

}

#endif

