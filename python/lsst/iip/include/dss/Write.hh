
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
 
#ifndef DSS_WRITE
#define DSS_WRITE

#include "dsi/Call.hh"

#include "dss/Store.hh"
#include "dss/Page.hh"

namespace DSS {

class Write : public DSI::Call {
public:                         
  Write(const Page&, const void* content, int sizeof_content, Store&);
public:
 ~Write() {} 
};
  
}

#endif

