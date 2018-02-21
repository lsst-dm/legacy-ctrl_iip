
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
 
#ifndef DSS_RESTART
#define DSS_RESTART
 
#include "dsi/Call.hh" 

#include "dss/Store.hh"

namespace DSS {

class Restart : public DSI::Call {
public:
  Restart(Store&);
public:  
 ~Restart() {};
  }; 

}

#endif

