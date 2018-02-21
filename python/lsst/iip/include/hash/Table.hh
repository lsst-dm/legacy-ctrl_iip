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
 
#ifndef HASH_TABLE
#define HASH_TABLE

#include "hash/Element.hh"
#include "hash/List.hh"

namespace Hash {

class Table {
public:
  Table(uint32_t stride) : _stride(stride-1), _table(new List[stride]), _end(_table + stride) {}
public:
 ~Table() {delete[] _table;}
public:
  unsigned length()   const {return _stride + 1;} 
  unsigned occupied(); 
public:
  int      insert(Element* element) {return _list(element->key())->insert(element);}  
  Element* lookup(uint64_t key)     {return _list(key)->lookup(key);}
  Element* remove(uint64_t key)     {return _list(key)->remove(key);}
public:
  List* seek(List*);
  List* seek() {return seek(_table);}
private:
  List* _list(uint64_t key) {return _table + (_stride & (uint32_t)key);}  
private:
  unsigned _stride;
  List*    _table;
  List*    _end;
};

}

#endif
