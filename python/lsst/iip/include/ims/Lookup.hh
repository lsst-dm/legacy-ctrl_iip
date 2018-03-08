
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
 
#ifndef DSS_LOOKUP
#define DSS_LOOKUP

#include "dsi/Symbol.hh"
#include "dsi/Call.hh"

#include "dss/Pid.hh"
#include "dss/Store.hh"

namespace DSS {

class Lookup : public DSI::Call {
public:                         
  Lookup(const DSI::Symbol&, Pid&, Store&);
public:
 ~Lookup() {}
public: 
  int error; 
};

}

#endif

 