
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
 
#ifndef DAQ_WAVEFRONTSET
#define DAQ_WAVEFRONTSET

#include "daq/LocationSet.hh"

namespace DAQ {

class __attribute__((__packed__)) WavefrontSet : public LocationSet {
public:  
  WavefrontSet(); 
public:
 ~WavefrontSet() {}
 };

}

#endif

