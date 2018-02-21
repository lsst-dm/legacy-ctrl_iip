
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
 
#ifndef HKS_CONSTANT
#define HKS_CONSTANT

#include "hks/Symbol.hh"

namespace HKS {

class __attribute__((__packed__)) Constant : public Symbol {
public:  
  Constant()                                     : Symbol(),     value()       {}
  Constant(const char* name)                     : Symbol(name), value()       {}
  Constant(const char* name, const char* _value) : Symbol(name), value(_value) {}
public:
 ~Constant() {}
public:
  Symbol value;             
 };

}


#endif

