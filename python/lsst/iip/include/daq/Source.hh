
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
 
#ifndef DAQ_SOURCE
#define DAQ_SOURCE

#include <stdint.h>

#include "dvi/Version.hh"
#include "daq/Location.hh"
#include "daq/Sensor.hh"
#include "rms/InstructionList.hh"

namespace DAQ {

class Source {
public:
  Source() {}
public:  
  Source(const char* platform, Sensor::Type, uint8_t path);
  Source(const Source&);
public:
 ~Source() {}
public:
  Source& operator=(const Source&);
public:
  uint8_t      schema;     
  uint8_t      path;
  Sensor::Type type;
private:  
  uint8_t  _reserved1; 
  uint32_t _reserved2; 
public:
  DVI::Version release;
public:  
  char platform[32];
private:
  uint64_t _reserved3;      
};

}

#endif

