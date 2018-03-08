
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
 
#ifndef DSI_PARTITION
#define DSI_PARTITION

#include "dsi/SymbolTable.hh"
#include "dsi/Set.hh"

namespace DSI {

class Partition {
public: 
  Partition(const char* name,             const char* path);
  Partition(const char* name, const Set&, const char* path);
public:
 ~Partition() {}
 public: 
  Set* lookup(unsigned service) {return &_vector[service];}    
public: 
  void modify(unsigned service, const Set* members);
private:
  void _flush(unsigned service, const Set* members);
private:
  const char* _path;
  const char* _name;
  Set         _vector[SymbolTable::MAX];
  };
      
}

#endif

