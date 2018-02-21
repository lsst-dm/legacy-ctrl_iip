
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
 
#ifndef RDS_CLIENT
#define RDS_CLIENT

#include "dsi/Exception.hh"
#include "dsi/Client.hh"

#include "rds/Event.hh"

namespace RDS {

class Client : public DSI::Client {
public: 
  Client(const char* partition) throw (DSI::Exception);     
public:
  virtual ~Client() {}
  };

}

#endif

