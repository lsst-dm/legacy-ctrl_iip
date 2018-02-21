
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
 
#ifndef HKS_LOOKUPINTERFACE
#define HKS_LOOKUPINTERFACE

#include "dsi/Location.hh"
#include "dsi/Call.hh"

#include "daq/Interface.hh"

#include "hks/Partition.hh"

namespace HKS {

class LookupInterface : public DSI::Call {
public:
  LookupInterface(Partition&);
  LookupInterface(Partition&, const DSI::Address*);
public: 
  bool wait(DSI::Location&, DAQ::Interface*, int& error);
public:
 ~LookupInterface() {}    
 };

}

#endif

