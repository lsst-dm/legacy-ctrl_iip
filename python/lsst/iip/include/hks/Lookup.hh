
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
 
#ifndef HKS_LOOKUPCONSTANT
#define HKS_LOOKUPCONSTANT

#include "dsi/Location.hh"
#include "dsi/Call.hh"

#include "hks/Symbol.hh"
#include "hks/Partition.hh"

namespace HKS {

class LookupConstant  {
public:
  LookupConstant(const Symbol&, Partition&);
  LookupConstant(const Symbol&, Partition&, const DSI::Address*);
public: 
  bool wait(DSI::Location&, Symbol*, int& error);
public:
 ~LookupConstant() {}
private:
  DSI::Call _lookup;    
 };

}

#endif

