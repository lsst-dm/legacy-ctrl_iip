
/*
**  Package:
**	
**
**  Abstract:
**    
** Beware: This is and must be an exact duplicate of the class by the same name found in INIT.  
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
 
#ifndef DAQ_MOUNTPOINTCACHE
#define DAQ_MOUNTPOINTCACHE

#include "daq/Mountpoint.hh"
#include "Cache.hh"

namespace DAQ {

class MountpointCache : public Mountpoint {
public:
  MountpointCache();                   
  MountpointCache(const MountpointCache&);      
public:
  MountpointCache& operator=(const Mountpoint&);
  MountpointCache& operator=(const MountpointCache&);
  MountpointCache& operator=(const char*);
public:
 ~MountpointCache() {}
public: 
  const char* value() const {return *this ? Mountpoint::value() : _fallback;} 
public:
  const char* local() const;
public:
  void reset();        
private:
  const char* _fallback;
  Cache       _cache;
 };

}

#endif

