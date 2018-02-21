
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
 
#ifndef IMS_PUBLISHER
#define IMS_PUBLISHER

#include "daq/LocationSet.hh"

#include "dss/Publisher.hh"
#include "dsi/Exception.hh"

namespace IMS {

class Publisher : public DSS::Publisher {
public:
  enum {MAX=128};
public: 
  Publisher(const char* partition, const char* group)                          throw (DSI::Exception);                        
  Publisher(const char* partition, const char* group, const DAQ::LocationSet&) throw (DSI::Exception);     
public:
 ~Publisher() {}
public:
  void interrupt(const char* message); 
private:
  char _group[MAX];  
};

}

#endif

