
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
 
#ifndef ARP_MEMBERS
#define ARP_MEMBERS

#include "net/Endian.hh"

#include "net/link/Address.hh"
#include "net/ipv4/Address.hh"

namespace ARP  {

class __attribute__((__packed__)) Members {
public:
  enum OpCode {REQUEST=1, REPLY=2};
public:
  Members(uint32_t             target, const IPV4::Address& sender); // Request...
  Members(const IPV4::Address& target, const IPV4::Address& sender); // Reply...
public:
 ~Members() {}
public: 
  bool valid(const IPV4::Address&) const;
public:   
  bool reply()   const {return Net::Endian::local(_opcode) == (uint16_t)REPLY;}  
  bool request() const {return Net::Endian::local(_opcode) == (uint16_t)REQUEST;}  
public: 
  uint32_t sender() const {return _sender_ipv4;} 
  uint32_t target() const {return _target_ipv4;} 
public: 
  const uint8_t* sender_link() const {return _sender_link;} 
  const uint8_t* target_link() const {return _target_link;} 
private:
  uint16_t _link_type; 
  uint16_t _ipv4_type;
  uint8_t  _link_length;
  uint8_t  _ipv4_length;
  uint16_t _opcode;
  uint8_t  _sender_link[6];
  uint32_t _sender_ipv4;
  uint8_t  _target_link[6];
  uint32_t _target_ipv4;
  };
 
}

#endif


