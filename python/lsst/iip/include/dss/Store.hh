
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
 
#ifndef DSS_STORE
#define DSS_STORE

#include "dsi/Exception.hh"
#include "dsi/Address.hh"
#include "dsi/Client.hh"
#include "dsi/Symbol.hh"

#include "dss/Repository.hh"
#include "dss/Exception.hh"
#include "dss/Attributes.hh"

namespace DSS {

class Store : public DSI::Client {
public: 
  Store(const char* partition) throw (DSI::Exception, Exception); 
  Store()                      throw (DSI::Exception, Exception);        
public:
 virtual ~Store() {}
private:
  friend class Lookup;
  friend class Open; 
  friend class Write;
  friend class Close; 
  friend class Sample;
  friend class Reset;
  friend class Shut;
  friend class Restart;
  friend class Remove;
private:
  friend class Stats;
  friend class RootId;
  friend class Transfer;
  friend class Name; 
public:
   const Repository& repository() const {return _attributes.repository;}     
private:  
  const DSI::Address* _server()    const {return &_attributes.address;}  
  uint8_t             _partition() const {return _attributes.pid.value();}     
private:
  Attributes _attributes; // Corresponding server attributes...
public:
  const char* __partition() const {return _gregg.name;} 
private:     
  DSI::Symbol _gregg;   
  };

}

#endif

