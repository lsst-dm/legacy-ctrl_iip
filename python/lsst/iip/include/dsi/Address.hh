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
 
#ifndef DSI_ADDRESS
#define DSI_ADDRESS

#include "dsi/Group.hh"
#include "dsi/Set.hh"

namespace DSI {

class __attribute__((__packed__)) Address : public Group {
public:
  Address()                                                         : Group(),                   space()            {}
public: 
  Address(const IPV4::Address& address, uint8_t location=0)         : Group(address),            space(location)    {}
  Address(const IPV4::Address& address, const Set& _space)          : Group(address),            space(_space)      {}  
public:  
  Address(unsigned service, unsigned partition, uint8_t location=0) : Group(service, partition), space(location)    {}
  Address(unsigned service, unsigned partition, const Set* _space)  : Group(service, partition), space(*_space)     {}
public:  
  Address(unsigned service, uint8_t location=0)                     : Group(service),            space(location)    {}
  Address(unsigned service, const Set* _space)                      : Group(service),            space(*_space)     {}  
public:    
  Address(const Address& clone)                                     : Group(clone),              space(clone.space) {}
public:
 ~Address() {}
public: 
  Address& operator =(const Address& clone) { Group::operator=(clone); space = clone.space; return *this;}       
public:
  Set space; 
};
 
}

#endif
