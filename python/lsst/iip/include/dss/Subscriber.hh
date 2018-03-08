
/*
**  Package:
**	
**
**  Abstract:
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
 
#ifndef DSS_SUBSCRIBER
#define DSS_SUBSCRIBER

#include "daq/LocationSet.hh"
#include "dsi/Subscriber.hh"

#include "dss/RootId.hh"
#include "dss/BranchId.hh"
#include "dss/LeafId.hh"
 
namespace DSS {

class Subscriber : public DSI::Subscriber {
public:
  Subscriber(const char* partition, const DAQ::LocationSet&) throw (DSI::Exception); 
public:  
  virtual ~Subscriber() {}
protected:
  virtual bool process(                                const RootId&)  = 0;
  virtual bool process(               const BranchId&, const RootId&)  = 0;
  virtual bool process(const LeafId&, const BranchId&, const RootId&)  = 0;  
private:
  bool M00(const void*, int); // Receive image bucket close notification
  bool M01(const void*, int); // Receive source bucket close notification
  bool M02(const void*, int); // Receive slice bucket close notification
  }; 

}

#endif

