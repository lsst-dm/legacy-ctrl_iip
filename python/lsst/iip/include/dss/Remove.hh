
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
 
#ifndef DSS_REMOVE
#define DSS_REMOVE

#include "dsi/Call.hh"

#include "dss/Name.hh"
#include "dss/Store.hh"

namespace DSS {

class Remove : public DSI::Call {
public:                         
  Remove(const Name&, Store&);
public:
 ~Remove() {}
public: 
  int error; 
  
};

}

#endif

 