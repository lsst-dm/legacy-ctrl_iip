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
 
#ifndef DSS_ELEMENT
#define DSS_ELEMENT

#include "hash/Element.hh"
#include "dss/RootId.hh"

namespace DSS {

class Element : public Hash::Element { 
public:
  Element(uint64_t key)                : Hash::Element(key), id()    {}
  Element(uint64_t key, const Id& _id) : Hash::Element(key), id(_id) {}
public:
 ~Element() {}
public:
  Element* flink() {return (Element*)Hash::Element::flink();} 
public:
  RootId id;
};

}

#endif
