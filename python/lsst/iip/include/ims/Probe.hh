
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
 
#ifndef IMS_PROBE
#define IMS_PROBE

#include "dsi/Address.hh"
#include "dsi/Call.hh"

#include "ims/Client.hh"

namespace IMS {

class Probe : public DSI::Call {
public:                         
  Probe(DSI::Address&, Client&);
public:
 ~Probe() {}
public:
  int error;  
};

}

#endif

 