
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
 
#ifndef DAQ_INTERFACECACHE
#define DAQ_INTERFACECACHE

#include "daq/Interface.hh"
#include "Cache.hh"

namespace DAQ {

class InterfaceCache : public Interface {
public:
  InterfaceCache();                   
  InterfaceCache(const InterfaceCache&);      
public:
  InterfaceCache& operator=(const Interface&);
  InterfaceCache& operator=(const InterfaceCache&);
public:
 ~InterfaceCache() {} 
public:
  void reset(); 
private:
  Cache _cache;
 };

}

#endif

