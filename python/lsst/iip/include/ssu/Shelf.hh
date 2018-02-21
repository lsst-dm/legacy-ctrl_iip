
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
 
#ifndef SSU_SHELF
#define SSU_SHELF

#include "dsi/Client.hh"

namespace SSU {

class Shelf : public  DSI::Client {
public:                         
  Shelf();
public:
 ~Shelf() {}
public:
  void reboot(); 
  };

}

#endif

