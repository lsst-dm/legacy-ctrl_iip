
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
 
#ifndef DSS_SHUT
#define DSS_SHUT
 
#include "dsi/Call.hh" 

#include "dss/Store.hh"

namespace DSS {

class Shut : public DSI::Call {
public:
  Shut(Store&);
public:  
 ~Shut() {};
  }; 

}

#endif

