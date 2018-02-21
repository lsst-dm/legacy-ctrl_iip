
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
 
#ifndef RDS_EVENT
#define RDS_EVENT

#include <stdint.h>

#include "daq/Sensor.hh"
#include "rms/InstructionList.hh"
#include "rds/ImageId.hh"

namespace RDS {
 
class __attribute__((__packed__)) Event {
public:
  Event(); 
  Event(const Event&);  
public:
 ~Event() {}
public: 
  Event& operator=(const Event&); 
public: 
  Event& operator=(const ImageId& image);
public: 
  const ImageId& image() const {return _image;}
public:
  RMS::InstructionList& science()   {return _client[(int)DAQ::Sensor::Type::SCIENCE];}
  RMS::InstructionList& wavefront() {return _client[(int)DAQ::Sensor::Type::WAVEFRONT];}    
  RMS::InstructionList& guiding()   {return _client[(int)DAQ::Sensor::Type::GUIDING];} 
public:
  const RMS::InstructionList& instructions(DAQ::Sensor::Type type) const {return _client[(int)type];}
  const RMS::InstructionList& instructions()                       const {return _system;}        
private:
  RMS::InstructionList _client[(int)DAQ::Sensor::Type::NUMOF];
  RMS::InstructionList _system;
private:
  ImageId _image;
 };

}

#endif

