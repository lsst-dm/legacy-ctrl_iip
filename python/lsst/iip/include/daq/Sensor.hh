
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
 
#ifndef DAQ_SENSOR
#define DAQ_SENSOR

#include <stdint.h>

namespace DAQ {

class Sensor {
public:
  enum class Type    : uint8_t  {NUMOF=3, SCIENCE=2, GUIDING=1, WAVEFRONT=0, UNDEFINED=0xFF};
  enum class Pixel   : unsigned {SIZEOF=18};                                                                // in units of bits    
  enum class Segment : unsigned {NUMOF=16, MIN=0, MAX=NUMOF-1, SIZEOF=(NUMOF * (unsigned)Pixel::SIZEOF)/8}; // per CCD (in units of bytes)
};

}

#endif

