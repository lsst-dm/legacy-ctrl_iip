
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
 
#ifndef HKS_LOOKUPROLE
#define HKS_LOOKUPROLE

#include "dsi/Location.hh"
#include "dsi/Call.hh"

#include "daq/Role.hh"
#include "hks/Partition.hh"

namespace HKS {

class LookupRole  : public DSI::Call {
public:
  LookupRole(Partition&);
  LookupRole(Partition&, const DSI::Address*);
public: 
  bool wait(DSI::Location&, DAQ::Role*, int& error);
public:
 ~LookupRole() {}    
 };

}

#endif

