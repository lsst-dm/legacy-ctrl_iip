
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
 
#ifndef HKS_LOOKUPPATH
#define HKS_LOOKUPPATH

#include "dsi/Location.hh"
#include "dsi/Call.hh"

#include "daq/Path.hh"
#include "hks/Partition.hh"

namespace HKS {

class LookupPath  : public DSI::Call {
public:
  LookupPath(Partition&);
  LookupPath(Partition&, const DSI::Address*);
public: 
  bool wait(DSI::Location&, DAQ::Path*, int& error);
public:
 ~LookupPath() {}    
 };

}

#endif

