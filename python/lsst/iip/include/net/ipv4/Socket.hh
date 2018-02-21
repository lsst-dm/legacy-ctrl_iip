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
 
#ifndef IPV4_SOCKET
#define IPV4_SOCKET

#include "net/ipv4/Address.hh"
#include "net/ipv4/Interface.hh"
#include "net/ipv4/Exception.hh"
#include "net/ipv4/SetException.hh"
#include "net/ipv4/JoinException.hh"

#include <sys/socket.h> // For socket options...
#include <netinet/in.h> // For socket IP options...

#if defined(__rtems__)
#include "net/rce/Plugin.hh" 
#endif

namespace IPV4 {

class Socket {
public:
  enum {SUCCESS=0, TIMEOUT=0, INTERUPTED=-1};
public: 
  Socket(const Interface*, uint16_t port, int tmo=0) throw(Exception);;  
  Socket(const Interface*,                int tmo=0) throw(Exception);;    
public:
 ~Socket();
public:
  Address address;
public:
  void join(uint32_t mcst_group) throw(JoinException);
public:
  void set(  int option, int value)   throw(SetException);
  void set(  int option)              throw(SetException); 
  void clear(int option)              throw(SetException);
public: 
  void setIp(  int option, int value) throw(SetException);
  void setIp(  int option)            throw(SetException); 
  void clearIp(int option)            throw(SetException);       
public:
 void sendTo(const Address*,                                                                                             const void* payload, unsigned sizeof_payload);
 void sendTo(const Address*, const void* header1, unsigned sizeof_header1,                                               const void* payload, unsigned sizeof_payload);
 void sendTo(const Address*, const void* header1, unsigned sizeof_header1, const void* header2, unsigned sizeof_header2, const void* payload, unsigned sizeof_payload);   
public:  
  int recv(                                      void* payload, unsigned sizeof_payload, Address* dst=(Address*)0);  
  int recv(void* header, unsigned sizeof_header, void* payload, unsigned sizeof_payload, Address* dst=(Address*)0);    
private:
  int _socket;
#if defined(__rtems__)
  unsigned    _mtu;
  RCE::Plugin _plugin;
#endif     
};

}

#endif