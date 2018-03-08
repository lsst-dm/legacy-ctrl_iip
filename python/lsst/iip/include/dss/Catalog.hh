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
 
#ifndef DSS_CATALOG
#define DSS_CATALOG

#include <stdint.h>

#include "dss/Id.hh"
#include "dss/Table.hh"
#include "dss/Element.hh"

namespace DSS {

class Catalog {
public:
  Catalog(const char* repository, const char* partition);
public:
 ~Catalog();
public:
  Element* insert( const char* name);
  Element* insert( const char* name, const Id&);
  Element* lookup( const char* name);    
  Element* remove( const char* name);
public:
  int dump(); 
private:
  uint64_t _hash(const char* name) const;      
private:
  Table _table;
};

}

#endif
