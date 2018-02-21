
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
 
#ifndef IMS_STRIPE
#define IMS_STRIPE

#include <stdint.h>

#include "daq/Sensor.hh"

namespace IMS {

class Stripe {
public:
  Stripe() {}     
public:
 ~Stripe() {}
public:
  int32_t segment[(unsigned)DAQ::Sensor::Segment::NUMOF]; 
 };

}

#endif

