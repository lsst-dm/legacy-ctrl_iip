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

#ifndef DSI_LIST
#define DSI_LIST

#include "hash/List.hh"
#include "dsi/Element.hh"

namespace DSI {

class List : public Hash::List {
public:
  List() : Hash::List() {}  
public:
 ~List() {}
 };

}

#endif

