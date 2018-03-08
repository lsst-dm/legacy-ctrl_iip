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
**	000 - January 09, 2007
**
**  Revision History:
**	None.
**
** --
*/
 
#ifndef DSI_SERVICE
#define DSI_SERVICE

#include "dsi/Symbol.hh"

namespace DSI {

class __attribute__((__packed__)) Service : public Symbol {
public:
  Service()                                             : Symbol(),         partition()           {} 
  Service(const char* _service, const char* _partition) : Symbol(_service), partition(_partition) {} 
public:
 ~Service() {}
public:
  Symbol partition;
};

}

#endif
