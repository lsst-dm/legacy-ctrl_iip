
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
 
#ifndef DSS_PUBLISHER
#define DSS_PUBLISHER

#include "daq/Location.hh"
#include "daq/LocationSet.hh"

#include "dsi/Publisher.hh"
#include "dsi/Exception.hh"

namespace DSS {

class Publisher : public DSI::Publisher {
public:                         
  Publisher(const char* partition, const DAQ::Location&)    throw (DSI::Exception); 
  Publisher(const char* partition, const DAQ::LocationSet&) throw (DSI::Exception);     
public:
 ~Publisher() {} 
};

}

#endif

