
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
 
#ifndef DSI_CLIENT
#define DSI_CLIENT

#include "dsi/Socket.hh"
#include "dsi/Exception.hh"
#include "dsi/Set.hh"
#include "dsi/Symbol.hh"

namespace DSI {

class Client : public Socket {
protected: 
  Client(const char* service, const char* partition) throw (Exception);                               
public:
 ~Client() {}
public:
  const char* partition() const {return _partition.name;}  
private:
  Symbol _partition;    
};
                 
}

#endif

