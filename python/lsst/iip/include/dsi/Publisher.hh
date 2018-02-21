
/*
**  Package:
**	
**
**  Abstract:
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
 
/*
**  Package:
**	
**
**  Abstract:
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
 
#ifndef DSI_PUBLISHER
#define DSI_PUBLISHER

#include "dsi/Address.hh"
#include "dsi/Socket.hh"
#include "dsi/Exception.hh"
#include "dsi/Set.hh"
#include "dsi/Symbol.hh"

namespace DSI {

class Publisher : public Socket {
protected: 
  Publisher(const char* service, const char* partition, const Set& sources) throw (Exception);                               
public:
 ~Publisher() {}
public:
  const char* partition() const {return _partition.name;} 
private:     
  Symbol _partition;   
};
                
}

#endif

