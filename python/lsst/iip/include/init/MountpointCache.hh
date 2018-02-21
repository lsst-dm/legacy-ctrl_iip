
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
 
#ifndef INIT_MOUNTPOINTCACHE
#define INIT_MOUNTPOINTCACHE

#include "init/Mountpoint.hh"

#include "Cache.hh"

namespace INIT {

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

