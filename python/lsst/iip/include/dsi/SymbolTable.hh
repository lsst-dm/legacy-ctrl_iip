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
 
#ifndef DSI_SYMBOLTABLE
#define DSI_SYMBOLTABLE

#include <stdint.h>

#include "dsi/Symbol.hh"

#include "dsi/Table.hh"
#include "dsi/Element.hh"
#include "dsi/FreeElements.hh"

namespace DSI {

class SymbolTable {
public:
  enum {MAX=32};
public:
  SymbolTable();
public:
 ~SymbolTable();
public:
  uint32_t assigned() const {return _assigned;}   
public:
  bool contains(unsigned index) const {return index < SymbolTable::MAX;}  
public:
  unsigned insert( const Symbol& symbol);
  unsigned lookup( const Symbol& symbol) {return symbol ? lookup(_hash(symbol)) : MAX;}   
  unsigned remove( const Symbol& symbol) {return symbol ? remove(_hash(symbol)) : MAX;}
public:
  unsigned lookup(uint64_t symbol);  
  unsigned remove(uint64_t symbol);  
private:
  unsigned _allocate();                
  void     _deallocate(unsigned index) { _assigned &= ~(1 << index);}      
public:
  int dump(); 
private:
  uint64_t _hash(const Symbol&) const;      
private:
  uint32_t     _assigned;
  uint32_t     _pad;
  Element*     _elements;
  Table        _table;
  FreeElements _freelist; 
};

}

#endif
