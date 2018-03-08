
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
 
#ifndef IPV4_MEMBERS
#define IPV4_MEMBERS

#include "net/Endian.hh"
#include "net/ipv4/Address.hh"

namespace IPV4  {

class  Members {
public:
  enum {ICMP=1, IGMP=2, TCP=6, UDP=17};
  enum {MF=(1 << 13)}; // flags - More Fragments
  enum {DF=(1 << 14)}; // flags - Don't Fragment
public:
  Members(const Address* dst, const Address* src);
public:
 ~Members() {}
public:
  uint8_t  protocol() const {return _protocol;}
  uint16_t length()   const {return Net::Endian::local(_length);}
  uint16_t id()       const {return Net::Endian::local(_id);}  
  uint16_t offset()   const {return Net::Endian::local(_offset) & 0x1FFF;}
  bool     more()     const {return Net::Endian::local(_offset) & MF;} 
  uint16_t checksum() const {return _checksum;} 
public: 
  uint32_t src() const {return _src;} 
  uint32_t dst() const {return _dst;}
public: 
  uint16_t invalid() const;
public:  
  unsigned partialsum() const;
public:  
  void update(uint16_t length, uint16_t offset, unsigned partialsum, bool more);
private:
  uint8_t  _version;   // include both version (4) and size (5) 
  uint8_t  _tos;       // Type-Of-Service
  uint16_t _length;    // datagram length;
  uint16_t _id;        // sequence number
  uint16_t _offset;    // includes offset + flags
  uint8_t  _ttl;       // Time-To-Live
  uint8_t  _protocol;
  uint16_t _checksum; 
  uint32_t _src;
  uint32_t _dst; 
  uint32_t _padding;
  };
 
}

#endif


