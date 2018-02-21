
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
 
#ifndef DAQ_IMAGE
#define DAQ_IMAGE

#include "daq/LocationSet.hh"
#include "osa/TimeStamp.hh"
#include "dvi/Version.hh"

namespace DAQ {
 
class Image {
public:
  enum {MAX=63};
public:
  Image();   
  Image(const char* name, const LocationSet&, const OSA::TimeStamp&);
  Image(const Image&);
public:
 ~Image() {}
public: 
  Image& operator=(const Image&);
public:
  operator bool() const {return _name[0];}     
public:
  const char* name() const {return _name;}  
public:
  OSA::TimeStamp creation; 
  DVI::Version   release;        
  LocationSet    sources; 
public:
  char _name[MAX+1];   
 };

}

#endif

