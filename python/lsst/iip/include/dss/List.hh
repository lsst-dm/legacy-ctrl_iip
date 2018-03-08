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

#ifndef DSS_LIST
#define DSS_LIST

#include "hash/List.hh"
#include "dss/Element.hh"

namespace DSS {

class List : public Hash::List {
public:
  List() : Hash::List() {}  
public:
 ~List() {}
 };

}

#endif

