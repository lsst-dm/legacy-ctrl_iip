
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
 
#ifndef DAQ_SCIENCESET
#define DAQ_SCIENCESET

#include "daq/LocationSet.hh"

namespace DAQ {

class __attribute__((__packed__)) ScienceSet : public LocationSet {
public:  
  ScienceSet(); 
public:
 ~ScienceSet() {}
private:
  void _register(uint8_t bay); 
 };

}

#endif

