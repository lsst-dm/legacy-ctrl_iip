
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
 
#ifndef DAQ_PATHCACHE
#define DAQ_PATHCACHE

#include "daq/Path.hh"
#include "Cache.hh"

namespace DAQ {

class PathCache : public Path {
public:
  PathCache();                   
  PathCache(const PathCache&);      
public:
  PathCache& operator=(const Path&);
  PathCache& operator=(const PathCache&);
  PathCache& operator=(const char*);
public:
 ~PathCache() {}
public: 
  const char* value() const {return *this ? Path::value() : _fallback;} 
public:
  void reset();        
private:
  const char* _fallback;
  Cache       _cache;
 };

}

#endif

