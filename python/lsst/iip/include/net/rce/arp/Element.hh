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
 
#ifndef ARP_ELEMENT
#define ARP_ELEMENT

#include <inttypes.h>
#include <stddef.h>

#include "linked/Element.hh"
#include "net/link/Address.hh"
 
namespace ARP {

class Element : public Linked::Element {
public:
  Element()                                           : Linked::Element()                                               {}
  Element(uint32_t key, const Link::Address& address) : Linked::Element(), _address(address), _key(key), _sequence(key) {} 
public:
  Element* flink() {return (Element*)Linked::Element::flink();}   
public:
 ~Element() {}
public:
  const Link::Address& address() const {return _address;} 
public:
  uint32_t key() const {return _key;}
private:
  Link::Address _address;
  uint8_t       _pad[2];
  uint32_t      _key;
  uint32_t      _sequence; 
};

}

#endif
