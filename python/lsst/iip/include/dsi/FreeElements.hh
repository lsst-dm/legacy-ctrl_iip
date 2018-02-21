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

#ifndef DSI_FREEELEMENTS
#define DSI_FREEELEMENTS

#include "linked/List.hh"
#include "dsi/Element.hh"

namespace DSI {

class FreeElements : public Linked::List {
public:
  FreeElements() : Linked::List() {} 
public:
 ~FreeElements() {}
public:
  Element* head()   {return (Element*)Linked::List::head();} 
  Element* tail()   {return (Element*)Linked::List::tail();}   
  Element* last()   {return (Element*)Linked::List::last();}    
  Element* remove() {return (Element*)Linked::List::remove();}
};

}

#endif

