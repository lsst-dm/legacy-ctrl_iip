
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
 
#ifndef DAQ_ROLECACHE
#define DAQ_ROLECACHE

#include "daq/Role.hh"
#include "Cache.hh"

namespace DAQ {

class RoleCache : public Role {
public:
  RoleCache();                   
  RoleCache(const RoleCache&);      
public:
  RoleCache& operator=(const Role&);
  RoleCache& operator=(const RoleCache&);
  RoleCache& operator=(const char*);
public:
 ~RoleCache() {}
public: 
  const char* value() const {return *this ? Role::value() : _fallback;} 
public: 
  const char* fallback() const {return _fallback;} 
public:
  void reset();        
private:
  const char* _fallback;
  Cache       _cache;
 };

}

#endif

