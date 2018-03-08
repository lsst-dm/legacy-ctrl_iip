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
 
#ifndef DSI_ELEMENT
#define DSI_ELEMENT

#include "hash/Element.hh"

namespace DSI {

class Element : public Hash::Element { 
public:
  Element()                      : Hash::Element()                           {}  
  Element(uint64_t key, unsigned _index) : Hash::Element(key), index(_index) {}
public:
 ~Element() {}
public:
  Element* flink() {return (Element*)Hash::Element::flink();} 
public:
  unsigned index;
};

}

#endif
