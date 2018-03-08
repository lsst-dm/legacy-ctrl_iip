/*
** ++
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
**	000 - January 09, 2007
**
**  Revision History:
**	None.
**
** --
*/
 
#ifndef DAQ_PREFERENCES
#define DAQ_PREFERENCES

#include "dsi/Set.hh"

#include "daq/DirectoryCache.hh"
#include "daq/MountpointCache.hh"
#include "daq/PartitionCache.hh"
#include "daq/RoleCache.hh"
#include "daq/PathCache.hh"
#include "daq/InterfaceCache.hh"

namespace SSU {class Server;} // Forward reference... 
namespace HKS {class Server;} // Forward reference... 

namespace DAQ {

class Preferences {
public:
  static Preferences* setup();
  static Preferences* lookup();
public:  
  static const char* myPartition();
public:
  Preferences();
public:
 ~Preferences() {}
public:
  const char* directory()  const {return _directory.value();}  
  const char* mountpoint() const {return _mountpoint.value();}
  const char* partition()  const {return _partition.value();}
  const char* role()       const {return _directory ? _role.value() : _role.fallback();}
  const char* path()       const {return _path.value();}   
public:  
  const Interface& interface() const {return _interface;}
  const DSI::Set&  space()     const {return _space;}
  int   lane()                 const {return _path.lane();}   
public:
  bool partitioned() const {return _partition;}   
private:
  friend class SSU::Server;
  friend class HKS::Server;
private:
  DirectoryCache  _directory;
  MountpointCache _mountpoint;
  PartitionCache  _partition;
  RoleCache       _role;
  PathCache       _path;
  InterfaceCache  _interface;
  DSI::Set        _space;
};

}
 
#endif

