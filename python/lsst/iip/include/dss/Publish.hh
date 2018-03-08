
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
 
#ifndef DSS_PUBLISH
#define DSS_PUBLISH

#include "dss/Publisher.hh"
#include "dss/RootId.hh"
#include "dss/BranchId.hh"
#include "dss/LeafId.hh"

#include "dsi/Call.hh"

namespace DSS {

class Publish : public DSI::Call {
public:                         
  Publish(const RootId&,   Publisher&);
  Publish(const BranchId&, Publisher&);
  Publish(const LeafId&,   Publisher&);
public:
 ~Publish() {}
};

}

#endif

 