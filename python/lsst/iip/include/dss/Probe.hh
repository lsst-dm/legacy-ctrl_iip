
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
 
#ifndef DSS_PROBE
#define DSS_PROBE

#include "dsi/Symbol.hh"
#include "dss/Attributes.hh"
#include "dsi/Call.hh"

#include "dss/Store.hh"

namespace DSS {

class Probe : public DSI::Call {
public:                         
  Probe(const DSI::Symbol&, Attributes&, Store&);
public:
 ~Probe() {}
public:
  int error;  
};

}

#endif

 