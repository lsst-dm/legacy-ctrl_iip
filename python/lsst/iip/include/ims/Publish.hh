
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
 
#ifndef IMS_PUBLISH
#define IMS_PUBLISH

#include "ims/Publisher.hh"

#include "dsi/Call.hh"

namespace IMS {

class Publish : public DSI::Call {
public:                         
  Publish(const Message&, Publisher&);
public:
 ~Publish() {}
};

}

#endif

 