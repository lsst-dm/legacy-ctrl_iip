
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
 
#ifndef SSU_LOOKUP
#define SSU_LOOKUP

#include "dsi/Address.hh"
#include "dsi/Location.hh"
#include "dsi/Call.hh"
#include "daq/Partition.hh"

#include "ssu/Shelf.hh"

namespace SSU {

class Lookup : public DSI::Call {
public:
  Lookup(Shelf&);
  Lookup(Shelf&, const DSI::Address*);
public: 
  bool wait(DSI::Location&, DAQ::Partition*, int& error);
public:
 ~Lookup() {}
 };

}

#endif

