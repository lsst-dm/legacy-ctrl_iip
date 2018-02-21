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
 
#ifndef DSI_NAMESPACE
#define DSI_NAMESPACE

#include "dsi/Symbol.hh"

#include "osa/File.hh"
#include "dsi/SymbolTable.hh"

namespace DSI {

class NameSpace {
public:
  NameSpace(const char* path, const char* filename, const char* extension);
public:
 ~NameSpace();
public:
  bool contains(unsigned index) const {return _table.contains(index);} 
public:
  uint32_t assigned() const {return _table.assigned();}
public:
  Symbol* name(unsigned index=0) {return  index < SymbolTable::MAX ? &_vector[index] : (Symbol*)0;}
public:
  unsigned insert( const Symbol& symbol);
  unsigned resolve(const Symbol& symbol);
public:     
  unsigned lookup(const Symbol& symbol) {return _table.lookup(symbol);}   
public:
  unsigned lookup(uint64_t symbol) {return _table.lookup(symbol);}  
  unsigned remove(uint64_t symbol); 
private: 
  void _reinsert();   
private:
  Symbol*     _vector; 
  OSA::File   _file;
  SymbolTable _table;
};

}

#endif
