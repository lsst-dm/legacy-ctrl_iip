
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

#ifndef IMS_SLICEID
#define IMS_SLICEID

#include "dss/LeafId.hh"
#include "ims/SourceId.hh"

namespace IMS {

class __attribute__((__packed__)) SliceId : public DSS::LeafId {
public:  
  SliceId(const SourceId& clone, uint8_t slice=0) : LeafId(slice, clone) {}
  SliceId(const SliceId&  clone, uint8_t slice=0) : LeafId(slice, clone) {}                                                                    
public:
 ~SliceId() {} 
public:  
  SliceId& operator=(const SliceId& clone) {LeafId::operator=(clone); return *this;}
  SliceId& operator=(uint8_t slice)        {LeafId::operator=(slice); return *this;}
public:  
  void advance() {_advanceLeaf();} 
 };
 
}


#endif

