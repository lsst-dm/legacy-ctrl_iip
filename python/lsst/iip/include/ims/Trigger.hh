
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
 
#ifndef IMS_TRIGGER
#define IMS_TRIGGER

#include "osa/TimeStamp.hh"
#include "dsi/Call.hh"
#include "ims/Event.hh"

#include "ims/Client.hh"

namespace IMS {

class Trigger : public DSI::Call {
public:                         
  Trigger(const Event&, Client&);
public:
 ~Trigger() {}
public:
  OSA::TimeStamp time;
  int            error;  
};

}

#endif

 