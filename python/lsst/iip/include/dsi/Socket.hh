
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
 
#ifndef DSI_SOCKET
#define DSI_SOCKET

#include "net/ipv4/Address.hh"
#include "net/ipv4/Socket.hh"
#include "dsi/Frame.hh"
#include "dsi/Set.hh"
#include "dsi/Address.hh"
#include "dsi/Exception.hh"

namespace DSI {

class Socket {
protected: 
  Socket();                               
public:
 ~Socket() {delete _socket;} 
public:
  Address service; 
public:
  const IPV4::Address& address() const {return _socket->address;}
public:
  uint8_t pid() const {return _pid;}  
protected:  
  unsigned _pid;
  unsigned _numof; 
protected:
  IPV4::Socket* _socket;    
private:
  friend class Call;  
private:
  uint32_t _transaction() {return _sequence++;}         
private:  
  void _sendTo(const Frame&);
  void _sendTo(const Frame&,                                        const void* payload, int sizeof_payload);
  void _sendTo(const Frame&, const void* header, int sizeof_header, const void* payload, int sizeof_payload);
private:
  void _sendTo(const Address* address, const Frame&);
  void _sendTo(const Address* address, const Frame&,                                        const void* payload, int sizeof_payload);
  void _sendTo(const Address* address, const Frame&, const void* header, int sizeof_header, const void* payload, int sizeof_payload); 
private:
   int _recv(Frame&);
   int _recv(Frame&, void* payload, int sizeof_payload);
private:
  uint32_t _sequence;
  };

}

#endif

