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
 
#ifndef DSI_MEMBERS
#define DSI_MEMBERS

#include "dsi/Set.hh"
#include "dsi/Service.hh"

namespace DSI {

class __attribute__((__packed__)) Members : public Set {
public:
  Members()                                                                 : Set(),        service()                     {} 
  Members(const char* _service, const char* _partition)                     : Set(),        service(_service, _partition) {} 
  Members(const Set& members, const char* _service, const char* _partition) : Set(members), service(_service, _partition) {} 
public:
 ~Members() {}
public:
  Service service;
};

}

#endif
