
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
 
#ifndef RDS_TRIGGER
#define RDS_TRIGGER

#include "dsi/Call.hh"

#include "rds/Event.hh"
#include "rds/Client.hh"

namespace RDS {

class Trigger : public DSI::Call {
public:                         
  Trigger(const Event&, Client&);
public:
 ~Trigger() {}
};

}

#endif

 