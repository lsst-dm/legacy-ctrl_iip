
/*
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
**	    000 - April 06, 2011
**
**  Revision History:
**	    None.
**
** --
*/
 
#ifndef LINK_ADDRESS
#define LINK_ADDRESS

#include <stdint.h>

namespace Link {

class __attribute__((__packed__)) Address {
public:
  static char* presentation(const uint8_t* address, char* buffer); 
public:
  Address();
  Address(uint64_t all);
  Address(const uint8_t* address);
  Address(uint32_t ipv4);
  Address(const char* address);
  Address(const Address&); 
public:
  Address& operator=(const Address&); 
  Address& operator=(uint64_t); 
  Address& operator=(const uint8_t*); 
  Address& operator=(uint32_t);                                                                                                         
public:
 ~Address() {}
public:
  uint64_t id() const {return _address.id;} 
public:
  bool valid() const;
public:
  char* presentation(char* buffer) const;
public:
  void set(uint8_t*) const;  
private:   
  void _lookup(uint32_t ipv4);
private:
  union {uint8_t byte[8]; uint64_t id;}  _address;
  };

}

#endif




