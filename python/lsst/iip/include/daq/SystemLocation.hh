
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
 
#ifndef DAQ_SYSTEMLOCATION
#define DAQ_SYSTEMLOCATION

#include "daq/Location.hh"

namespace DAQ {

class __attribute__((__packed__)) SystemLocation : public Location {
public:  
  SystemLocation()                            : Location(Location::SYSTEM, (uint8_t)0) {} 
  SystemLocation(const SystemLocation& clone) : Location(clone)                        {}
public:
 ~SystemLocation() {}
public:  
  SystemLocation& operator=(const SystemLocation& clone) {Location::operator=(clone); return *this;}  
 };

}

#endif

