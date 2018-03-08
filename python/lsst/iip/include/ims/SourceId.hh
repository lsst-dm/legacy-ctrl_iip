
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

#ifndef IMS_SOURCEID
#define IMS_SOURCEID

#include "dss/BranchId.hh"
#include "daq/Location.hh"
#include "ims/ImageId.hh"

namespace IMS {

class __attribute__((__packed__)) SourceId : public DSS::BranchId {
public:  
  SourceId(const ImageId& clone, const DAQ::Location& source) : DSS::BranchId(source.index(), clone) {}                                   
public:
 ~SourceId() {} 
public:  
  SourceId& operator=(const SourceId& clone)       {DSS::BranchId::operator=(clone);          return *this;}
  SourceId& operator=(const DAQ::Location& source) {DSS::BranchId::operator=(source.index()); return *this;}
 };
 
}


#endif

