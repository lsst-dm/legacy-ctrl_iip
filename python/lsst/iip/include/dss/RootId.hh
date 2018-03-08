
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

#ifndef DSS_ROOTID
#define DSS_ROOTID

#include "dss/Store.hh"
#include "dss/Id.hh"

namespace DSS {

class __attribute__((__packed__)) RootId : public Id {
public:  
  RootId()             : Id()   {_encodeRoot();}
  RootId(const Id& id) : Id(id) {_encodeRoot();}
  RootId(uint64_t id)  : Id(id) {}                                                               
public:
  RootId(const char* name, Store&);
public:
  void remove();                                                                  
public:
 ~RootId() {} 
 };

}

#endif

