
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
 
#ifndef ARP_FRAME
#define ARP_FRAME

#include "net/ipv4/Address.hh"
#include "net/link/Members.hh"
#include "net/rce/arp/Members.hh"
#include "net/link/Frame.hh"

namespace ARP  {

class __attribute__((__packed__)) Frame : public Link::Frame {
public:
  Frame(uint32_t             target,  const IPV4::Address& sender);
  Frame(const IPV4::Address& target,  const IPV4::Address& sender); 
public:
 ~Frame() {}
public:
  Members arp;
private:
  uint8_t _pad[6];  
//private:
//  uint8_t _pad[60 - (sizeof(Members) + sizeof(Link::Frame))];   
  };

/*
** ++
**
** Request...
**
** --
*/

inline Frame::Frame(uint32_t target, const IPV4::Address& sender) : 
 Link::Frame(sender.link(), (uint16_t)Link::Frame::ARP), 
 arp(target, sender) 
 {
 }
 
/*
** ++
**
** Reply...
**
** --
*/

inline Frame::Frame(const IPV4::Address& target, const IPV4::Address& sender) : 
 Link::Frame(target.link(), sender.link(), (uint16_t)Link::Frame::ARP), 
 arp(target, sender) 
 {
 }
  
}

#endif


