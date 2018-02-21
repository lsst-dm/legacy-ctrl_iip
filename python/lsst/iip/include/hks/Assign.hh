
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
 
#ifndef HKS_ASSIGN
#define HKS_ASSIGN

#include "dsi/Location.hh"
#include "dsi/Call.hh"
#include "dsi/Address.hh"

#include "daq/Mountpoint.hh"
#include "daq/Release.hh"
#include "daq/Role.hh"
#include "daq/Path.hh"
#include "daq/Interface.hh"

#include "hks/Partition.hh"

namespace HKS {

class Assign : public DSI::Call {
public:
  Assign(const DAQ::Release&, Partition&);
  Assign(const DAQ::Release&, Partition&, const DSI::Address*);
public:
  Assign(const DAQ::Mountpoint&, Partition&);
  Assign(const DAQ::Mountpoint&, Partition&, const DSI::Address*); 
public:
  Assign(const DAQ::Role&, Partition&);
  Assign(const DAQ::Role&, Partition&, const DSI::Address*); 
public:
  Assign(const DAQ::Path&, Partition&);
  Assign(const DAQ::Path&, Partition&, const DSI::Address*);
public:
  Assign(const DAQ::Interface&, Partition&);
  Assign(const DAQ::Interface&, Partition&, const DSI::Address*);            
public: 
  bool wait(DSI::Location&, int& error);
public:
 ~Assign() {}   
 };

}

#endif

