
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
 
#ifndef HKS_LOOKUPMOUNTPOINT
#define HKS_LOOKUPMOUNTPOINT

#include "dsi/Location.hh"
#include "dsi/Call.hh"

#include "daq/Mountpoint.hh"

#include "hks/Partition.hh"

namespace HKS {

class LookupMountpoint  : public DSI::Call {
public:
  LookupMountpoint(Partition&);
  LookupMountpoint(Partition&, const DSI::Address*);
public: 
  bool wait(DSI::Location&, DAQ::Mountpoint*, int& error);
public:
 ~LookupMountpoint() {}
 };

}

#endif

