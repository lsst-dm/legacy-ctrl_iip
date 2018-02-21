
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
 
#ifndef HKS_RESET
#define HKS_RESET

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

class Reset : public DSI::Call {
public:
  Reset(const DAQ::Release&, Partition&);
  Reset(const DAQ::Release&, Partition&, const DSI::Address*);
public:
  Reset(const DAQ::Mountpoint&, Partition&);
  Reset(const DAQ::Mountpoint&, Partition&, const DSI::Address*); 
public:
  Reset(const DAQ::Role&, Partition&);
  Reset(const DAQ::Role&, Partition&, const DSI::Address*); 
public:
  Reset(const DAQ::Path&, Partition&);
  Reset(const DAQ::Path&, Partition&, const DSI::Address*);
public:
  Reset(const DAQ::Interface&, Partition&);
  Reset(const DAQ::Interface&, Partition&, const DSI::Address*);            
public: 
  bool wait(DSI::Location&, int& error);
public:
 ~Reset() {}   
 };

}

#endif

