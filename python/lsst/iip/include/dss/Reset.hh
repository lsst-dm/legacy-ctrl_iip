
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
 
#ifndef DSS_RESET
#define DSS_RESET

#include "dsi/Call.hh"

#include "dss/Pid.hh"
#include "dss/Store.hh"

namespace DSS {

class Reset : public DSI::Call {
public:                         
  Reset(const Pid&, Store&); 
public:
 ~Reset() {}
public:
  int error;  
}; 
    
}

#endif

