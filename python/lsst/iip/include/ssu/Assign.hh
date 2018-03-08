
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
 
#ifndef SSU_ASSIGN
#define SSU_ASSIGN

#include "dsi/Location.hh"
#include "dsi/Call.hh"
#include "dsi/Address.hh"
#include "daq/Partition.hh"

#include "ssu/Shelf.hh"

namespace SSU {

class Assign  : public DSI::Call {
public:
  Assign(const DAQ::Partition&, Shelf&);
  Assign(const DAQ::Partition&, Shelf&, const DSI::Address*);
public: 
  bool wait(DSI::Location&, int& error);
public:
 ~Assign() {}
 };

}

#endif

