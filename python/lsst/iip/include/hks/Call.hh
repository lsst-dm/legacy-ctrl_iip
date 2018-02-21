
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
 
#ifndef HKS_ASSIGN
#define HKS_ASSIGN

#include "dsi/Location.hh"
#include "dsi/Call.hh"
#include "dsi/Address.hh"

#include "hks/Constant.hh"
#include "hks/Space.hh"
#include "hks/Partition.hh"

namespace HKS {

class Assign  {
public:
  Assign(const Constant&, Partition&);
  Assign(const Constant&, Partition&, const DSI::Address*);
public:
  Assign(const Space&, Partition&);
  Assign(const Space&, Partition&, const DSI::Address*); 
public: 
  bool wait(DSI::Location&, int& error);
public:
    
public:
 ~Assign() {}
private:
  DSI::Call _assign;    
 };

}

#endif

