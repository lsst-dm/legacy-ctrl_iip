
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
 
#ifndef DSS_SAMPLE
#define DSS_SAMPLE

#include "dsi/Call.hh"

#include "dss/Store.hh"
#include "dss/Stats.hh"
#include "dss/Pid.hh"

namespace DSS {

class Sample : public DSI::Call {
public:  
  Sample(const Pid&, Stats&, Store&);
public:
 ~Sample() {}
public:
 int error;
}; 
  
}

#endif

