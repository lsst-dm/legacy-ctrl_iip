
/*
**  Package:
**	
**
**  Abstract:
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
 
#ifndef DSI_CACHECORE
#define DSI_CACHECORE

#include "dsi/Symbol.hh"
#include "dsi/Service.hh"
#include "dsi/Members.hh"
#include "dsi/NameSpace.hh"
#include "dsi/Partition.hh"

namespace DSI {

class CacheCore {
public:
  CacheCore(const char* path, const char* service, const char* partition);
public:  
 ~CacheCore();
public:
  int32_t lookup(const Service*, void* buffer);
  int32_t probe( const Members*, void* buffer);
  int32_t modify(const Members*);   
private:
  void     _recache(unsigned partitions);
  unsigned _lookup(const Symbol&);
private:
  NameSpace   _services;
  NameSpace   _partitions;
  const char* _path;   
  Partition*  _partition[SymbolTable::MAX];
}; 

}

#endif

