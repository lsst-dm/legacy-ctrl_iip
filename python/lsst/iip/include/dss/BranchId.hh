
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

#ifndef DSS_BRANCHID
#define DSS_BRANCHID

#include "dss/Id.hh"

namespace DSS {

class LeafId; // Forward reference...

class __attribute__((__packed__)) BranchId : public Id {
public:  
  BranchId(uint8_t number, const Id& clone) : Id(clone) {_encodeBranch(number);} 
public:
 ~BranchId() {} 
public: 
  BranchId& operator=(uint8_t number)       {_encodeBranch(number); return *this;}
public:
  uint8_t number() const {return _decodeBranch();} 
public:
  void advance() {_advanceBranch();}   
 };

}

#endif

