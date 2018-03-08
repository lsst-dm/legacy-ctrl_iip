
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
 
#ifndef DSI_SHUT
#define DSI_SHUT
 
#include "dsi/Call.hh" 
#include "dsi/Address.hh"
#include "dsi/Client.hh"

namespace DSI {

class Shut : public Call {
public:
  Shut(Client& client)                         : Call(Call::SHUT, client)          {}
  Shut(Client& client, const Address* targets) : Call(Call::SHUT, client, targets) {}
public:  
 ~Shut() {};
  }; 

}

#endif

