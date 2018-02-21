
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
 
#ifndef HKS_SPACE
#define HKS_SPACE

#include "dsi/Set.hh"
#include "hks/Symbol.hh"

namespace HKS {

class __attribute__((__packed__)) Space : public Symbol {
public:  
  Space()                                         : Symbol(),     value()       {}
  Space(const char* name)                         : Symbol(name), value()       {}
  Space(const char* name, const DSI::Set& _value) : Symbol(name), value(_value) {}
public:
 ~Space() {}
public:
  DSI::Set value;             
 };

}


#endif

