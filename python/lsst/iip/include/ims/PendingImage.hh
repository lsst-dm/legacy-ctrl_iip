
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
 
#ifndef IMS_PENDINGIMAGE
#define IMS_PENDINGIMAGE

#include "ims/Image.hh"
#include "ims/Exception.hh"
#include "ims/PendingSource.hh"

#include "dss/RootId.hh"
#include "dss/BranchId.hh"
#include "dss/Repository.hh"

#include "daq/LocationSet.hh"

namespace IMS {

class PendingImage : public Linked::Element {
public:
  PendingImage(const DSS::RootId&, const DAQ::LocationSet& accepts, uint8_t system, const DSS::Repository&) throw(Exception); 
public:
 ~PendingImage() {}            
public:
  Image image; 
public:
  PendingSource* lookup(const DSS::BranchId&);
public:   
  void* allocate(const DSS::BranchId& branch) {return (void*)&_source[branch.number() * sizeof(PendingSource)];}
public:
  bool remaining() {return _remaining;} 
public:
  void retire(const DSS::BranchId& source) {_remaining.had(source.number());} 
public:
  DAQ::LocationSet _pending;
  DAQ::LocationSet _remaining;  
private:  
  char _source[sizeof(PendingSource) * 64];
};

}

#endif

