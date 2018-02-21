
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
 
#ifndef IMS_STORE
#define IMS_STORE

#include "dsi/Exception.hh"
#include "dss/Exception.hh"
#include "dss/Store.hh"

namespace IMS {

class Store : public DSS::Store {
public: 
  Store(const char* partition)  throw (DSI::Exception, DSS::Exception) : DSS::Store(partition) {}; 
public:
 virtual ~Store() {}
private:
  friend class Image;
  };

}

#endif

