
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

#ifndef DSS_LEAFID
#define DSS_LEAFID

#include "dss/Id.hh"

namespace DSS {

class __attribute__((__packed__)) LeafId : public Id {
public:  
  LeafId(uint8_t number, const Id& id) : Id(id) {_encodeLeaf(number);}
public:
 ~LeafId() {} 
public:  
  LeafId& operator=(uint8_t number) {_encodeLeaf(number); return *this;}
public:
  uint8_t number() const {return _decodeLeaf();}
  uint8_t branch() const {return _decodeBranch();}  
public:
  void advance() {_advanceBranch();}             
 };

}

#endif

