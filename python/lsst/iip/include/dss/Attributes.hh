
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
 
#ifndef DSS_ATTRIBUTES
#define DSS_ATTRIBUTES

#include "dsi/Address.hh"
#include "dss/Repository.hh"
#include "dss/Pid.hh"

#include <stdint.h>

namespace DSS {

class __attribute__((__packed__)) Attributes {
public:
  Attributes()                                                      : address(),               repository(),                 pid()     {} 
  Attributes(const DSI::Address& _address, const char* _repository) : address(_address),       repository(_repository),      pid()     {} 
  Attributes(const Attributes& clone, uint8_t _pid =0)              : address(clone.address),  repository(clone.repository), pid(_pid) {}
public:
 ~Attributes() {}
public:
  DSI::Address address;
  Repository   repository; 
  Pid          pid;
  };
  
}

#endif

