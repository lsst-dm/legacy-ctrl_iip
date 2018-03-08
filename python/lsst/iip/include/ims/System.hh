
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
 
#ifndef IMS_SYSTEM
#define IMS_SYSTEM

#include "rms/InstructionList.hh"
#include "ims/Client.hh"
#include "ims/Event.hh"
#include "dss/Store.hh"
#include "dss/Publisher.hh"
#include "rds/Event.hh"
#include "rds/Client.hh"

namespace IMS {

class System {
public:  
  System(const char* partition);
public:
 ~System() {}  
public:
  RMS::InstructionList& science()   {return _event.science();}
  RMS::InstructionList& wavefront() {return _event.wavefront();}    
  RMS::InstructionList& guiding()   {return _event.guiding();}    
public:
  int trigger(Event::Command);  
  int trigger(Event::Command, const char* image);
  int trigger(const char* image);
private:
  int _trigger(Event::Command, const char* image);
private:
  DSS::Store  _store;
  DSS::Publisher _publisher;
  IMS::Client _system;
  RDS::Client _partition;
  RDS::Event  _event;
 };

}

#endif

