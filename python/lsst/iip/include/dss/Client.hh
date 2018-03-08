
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
 
#ifndef DSS_CLIENT
#define DSS_CLIENT

#include "dsi/Symbol.hh"
#include "dsi/Address.hh"
#include "dsi/Publisher.hh"

#include "dss/Pid.hh"

namespace DSS {

class Client : public DSI::Publisher {
public:
  enum {PAGE_SIZE2 = 15}; // expressed as factor of 2 (32 KBytes)...
public:                         
  Client(const char* partition);     
public:
 virtual ~Client() {} 
public:
  const char*         repository() const {return _repository.name;}  
  const DSI::Address* server()     const {return &_server;}
public:  
  uint8_t partition() const {return _pid.value();}  
public:  
  const Pid* pid() const {return &_pid;} 
public:
  DSI::Address _server; // Single-cast address of server...
  DSI::Symbol  _repository;
  Pid          _pid;    
  };

}

#endif

