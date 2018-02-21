
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
 
#ifndef DSS_CLOSE
#define DSS_CLOSE

#include "dsi/Call.hh"

#include "dss/Store.hh"
#include "dss/Summary.hh"

namespace DSS {

class Close : public DSI::Call {
public:                         
  Close(const Summary&, Summary&, Store&);
public:
 ~Close() {}
public:
  int error;  
};
   
}

#endif

