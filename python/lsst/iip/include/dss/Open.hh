
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
 
#ifndef DSS_OPEN
#define DSS_OPEN

#include "dsi/Call.hh"

#include "dss/Store.hh"
#include "dss/Page.hh"
#include "dss/Name.hh"
#include "dss/Identifier.hh"

namespace DSS {

class Open : public DSI::Call {
public:                         
  Open(const Identifier&, Store&);
  Open(const Name&,       Store&);
public:
 ~Open() {}
public:
  Page id;
public:  
  int error;  
};

}

#endif


 
 
 
 
 