
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
 
#ifndef DSS_CREATE
#define DSS_CREATE

#include "dsi/Call.hh"

#include "dss/Store.hh"
#include "dss/Page.hh"
#include "dss/Name.hh"

namespace DSS {

class Create : public DSI::Call {
public:                         
  Create(const Name&, Store&);
public:
 ~Create() {}
public:
  Page id;
public:  
  int error;  
};

}

#endif


 
 
 
 
 