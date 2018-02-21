
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
 
#ifndef HKS_SHUT
#define HKS_SHUT
 
#include "dsi/Call.hh" 
#include "dsi/Address.hh"

#include "hks/Partition.hh"

namespace HKS {

class Shut : public DSI::Call {
public:
  Shut(Partition&);
  Shut(Partition&, const DSI::Address*);
public:  
 ~Shut() {};
  }; 

}

#endif

