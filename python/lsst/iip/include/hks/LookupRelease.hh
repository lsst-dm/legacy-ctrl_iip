
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
 
#ifndef HKS_LOOKUPRELEASE
#define HKS_LOOKUPRELEASE

#include "dsi/Location.hh"
#include "dsi/Call.hh"

#include "daq/Release.hh"

#include "hks/Partition.hh"

namespace HKS {

class LookupRelease  : public DSI::Call {
public:
  LookupRelease(Partition&);
  LookupRelease(Partition&, const DSI::Address*);
public: 
  bool wait(DSI::Location&, DAQ::Release*, int& error);
public:
 ~LookupRelease() {} 
 };

}

#endif

