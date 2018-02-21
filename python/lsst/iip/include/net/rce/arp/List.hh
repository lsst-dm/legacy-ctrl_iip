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
 
#ifndef ARP_LIST
#define ARP_LIST

#include "linked/List.hh"
#include "net/rce/arp/Element.hh"

namespace ARP {

class List {
public:
  List() : _list() {}  
public:
 ~List() {}
public:
  bool empty() {return _list.empty();}  
public:
  Element* head() {return (Element*)_list.head();}
  Element* last() {return (Element*)_list.last();}   
public:
 int insert(Element*);
public: 
 Element* lookup(uint32_t key);
 Element* remove(uint32_t);
private:
  Linked::List _list;  
 };
 
}	

#endif
