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
 
#ifndef ARP_FREELIST
#define ARP_FREELIST

#include "linked/List.hh"
#include "net/rce/arp/Element.hh"

namespace ARP  {

class FreeList {
public:
  FreeList(unsigned size); 
public:
 ~FreeList() {delete[] _elements;}
public:
  void* allocate()                   {return (void*)_freelist.remove();}
  void  deallocate(Element* element) {_freelist.insert(element);}
  void* empty()                      {return (void*)_freelist.last();}    
private:
  Linked::List _freelist;
  Element*     _elements;
};

}

#endif
