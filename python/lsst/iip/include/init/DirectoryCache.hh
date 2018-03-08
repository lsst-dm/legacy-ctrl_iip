
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
 
#ifndef INIT_DIRECTORYCACHE
#define INIT_DIRECTORYCACHE

#include "init/Directory.hh"

#include "Cache.hh"

namespace INIT {

class DirectoryCache : public Directory {
public:
  DirectoryCache();                   
  DirectoryCache(const DirectoryCache&);      
public:
  DirectoryCache& operator=(const Directory&);
  DirectoryCache& operator=(const DirectoryCache&);
  DirectoryCache& operator=(const char*);
public:
 ~DirectoryCache() {}
public: 
  const char* value() const {return *this ? Directory::value() : _fallback;} 
public:
  void reset();        
private:
  const char* _fallback;
  Cache       _cache;
 };

}

#endif

