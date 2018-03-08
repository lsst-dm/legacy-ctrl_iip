
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
 
#ifndef IMS_PENDINGSOURCE
#define IMS_PENDINGSOURCE

#include "ims/Source.hh"
#include "ims/Exception.hh"

#include "dss/BranchId.hh"
#include "dss/LeafId.hh"
#include "dss/Repository.hh"
#include "dsi/Set.hh"

namespace IMS {

class PendingSource : public Source {
public:
  PendingSource(const DSS::BranchId&, const DSS::Repository&) throw(Exception); 
public:
 ~PendingSource() {} 
public:
  bool processed(const DSS::LeafId& id); 
public:
  void lastIs(const DSS::LeafId& slice);
public:
  void retire(const DSS::LeafId& slice) {_remaining.had(slice.number());}             
public:
  bool remaining() {return _remaining;} 
private:
  DSI::Set _pending;
  DSI::Set _remaining;  
};

}

#endif

