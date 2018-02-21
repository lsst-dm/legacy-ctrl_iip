/*
** ++
**  Package:
**  
**
**  Abstract:
**
**  Author:
**      Michael Huffer, SLAC, (415) 926-4269
**
**  Creation Date:
**	000 - June 20 1,1997
**
**  Revision History:
**	None.
**
** --
*/

#ifndef LINKED_ELEMENT
#define LINKED_ELEMENT

namespace Linked {

class Element {
public:
  Element()                                              {}
  Element(Element* empty) : _flink(empty), _blink(empty) {}
public:
 ~Element() {} 
public:
  Element* flink() {return _flink;}
  Element* blink() {return _blink;}
public:  
  void link(Element* element) {Element* next = _flink; element->_flink = next; element->_blink = this; _flink = element; next->_blink = element;} // Inserts element AFTER this...
public:       
  void extract() {Element* next = _flink; Element* prev = _blink; prev->_flink = next; next->_blink = prev;} // Removes this...
protected:
  Element* _flink;
  Element* _blink;
};

}

#endif
