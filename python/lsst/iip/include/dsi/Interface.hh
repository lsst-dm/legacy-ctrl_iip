
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
 
#ifndef DSI_INTERFACE
#define DSI_INTERFACE

#include "net/ipv4/Socket.hh"
#include "net/ipv4/Interfaces.hh"
#include "net/ipv4/Interface.hh"
#include "net/ipv4/Address.hh"

#include "dsi/Set.hh"
#include "dsi/Members.hh"
#include "dsi/Frame.hh"
#include "dsi/Address.hh"

namespace DSI {
   
class Interface {
public:
  Interface(const char* service, const char* partition); 
  Interface(const char* service, const char* partition, const Set& members); 
  Interface(const char* service, const char* partition, const Set& members, const char* network); 
public:
 ~Interface() {}
public: 
  IPV4::Interface* interface();
public:
  Set& accepts() {return _request;}  
public:
  int32_t probe(IPV4::Address*);    
  int32_t lookup(Address*);  
public:
  int32_t assign(const Set&);
  int32_t remove(const Set&);
private: 
  int32_t _probe( IPV4::Interface*, IPV4::Address*);
  int32_t _lookup(IPV4::Interface*, Address*);
private: 
  int _wait(Frame*, IPV4::Socket&);    
  int _wait(Frame*, void* input, int sizeof_input, IPV4::Socket&);   
private:
  IPV4::Interfaces _interfaces;
  IPV4::Address    _cache;
  Members          _request;
  IPV4::Interface* _interface;
  uint32_t         _sequence;
  };

}

#endif


