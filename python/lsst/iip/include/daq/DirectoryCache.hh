
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
 
#ifndef DAQ_DIRECTORYCACHE
#define DAQ_DIRECTORYCACHE

#include "daq/Directory.hh"
#include "daq/Cache.hh"

namespace DAQ {

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

