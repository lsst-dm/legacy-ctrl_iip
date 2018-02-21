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

#ifndef LINKED_LIST
#define LINKED_LIST

#include "linked/Element.hh"

namespace Linked  {

class List : public Element {
public:
  List() : Element(this) {}
public:
 ~List() {} 
public: 
  bool empty() {return flink() == this;} 
public:
  Element* head() {return flink();} 
  Element* tail() {return blink();}  
  Element* last() {return this;}
public:   
  void insert(    Element* element) {Element* _tail = tail(); _tail->link(element);}  // at tail...
  void insertHead(Element* element) {Element* _head = this;   _head->link(element);}  // at head..
public:  
  Element* remove()     {Element* _head = head(); _head->extract(); return _head;}   // at head...
  Element* removeTail() {Element* _tail = tail(); _tail->extract(); return _tail;}   // at tail...
};

}

#endif

