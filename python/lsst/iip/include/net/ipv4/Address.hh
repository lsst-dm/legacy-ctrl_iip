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
**	000 - , 2007
**
**  Revision History:
**	None.
**
** --
*/
 
#ifndef IPV4_ADDRESS
#define IPV4_ADDRESS

#include <stdint.h>
//#include <sys/socket.h>
//#include <netinet/in.h>

#include "net/Endian.hh"

#include "net/ipv4/Exception.hh"
#include "net/link/Address.hh"
#include "net/ipv4/Interface.hh"

namespace IPV4 {
   
class __attribute__((__packed__)) Address {
public:
  static char* presentation(uint32_t address, char* buffer); 
public:
  Address();
  Address(uint32_t    address, uint16_t port=0);
  Address(const char* address, uint16_t port=0); 
  Address(const Interface*); 
public:  
  Address(int* socket, const Interface*, uint16_t port=0) throw(Exception); 
public:  
  Address(const Address&); 
public:  
  const Address& operator=(const Address& clone);  
public:  
  bool operator==(const Address& operand) {return operand._address.ipv4._addr == _address.ipv4._addr;} 
public:
 ~Address() {} 
public: 
  operator uint32_t() const {return _address.ipv4._addr;}    
public:
  operator bool() const {return _address.opaque != 0 ;} 
public:
  uint16_t             port()  const {return _address.ipv4._port;} 
  const Link::Address& link()  const {return _link;}  
public:
  uint32_t local()     const {return Net::Endian::local(_address.ipv4._addr);}
  uint32_t portLocal() const {return Net::Endian::local(_address.ipv4._port);}     
public:
  char* presentation(char* buffer)     const;
  char* portPresentation(char* buffer) const;
public:
  void print(int indent=0) const;
public:   
  void _recache();
public:
   unsigned family() const {return _address.ipv4._family;} 
private:   
  struct __attribute__((__packed__)) _Address {uint16_t _family; uint16_t _port; uint32_t _addr;};    
private:  
 union {struct _Address ipv4; uint64_t opaque;} _address;
 Link::Address                                  _link; 
};  

}

#endif
