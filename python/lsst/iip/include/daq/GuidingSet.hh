
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
 
#ifndef DAQ_GUIDINGSET
#define DAQ_GUIDINGSET

#include "daq/LocationSet.hh"

namespace DAQ {

class __attribute__((__packed__)) GuidingSet : public LocationSet {
public:  
  GuidingSet(); 
public:
 ~GuidingSet() {}
 };

}

#endif

