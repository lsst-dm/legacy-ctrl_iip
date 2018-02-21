
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
 
#ifndef IMS_CLIENT
#define IMS_CLIENT

#include "dsi/Exception.hh"
#include "dsi/Address.hh"
#include "dsi/Client.hh"

#include "ims/Event.hh"

namespace IMS {

class Client : public DSI::Client {
public: 
  Client() throw (DSI::Exception);     
public:
  virtual ~Client() {}
public:  
  void shut(); 
private:
  DSI::Address _server; // Single-cast address of server...     
  };

}

#endif

