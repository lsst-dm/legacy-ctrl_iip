
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
 
#ifndef IMS_SOURCE
#define IMS_SOURCE

#include "ims/Exception.hh"
#include "ims/Image.hh"
#include "ims/Store.hh"

#include "dss/Id.hh"

#include "dss/BranchId.hh"
#include "rms/InstructionList.hh"

#include "dvi/Version.hh"
#include "daq/Location.hh"
#include "dss/StoredBucket.hh"
#include "dss/Repository.hh"

namespace IMS {

class Source {
public:
  Source(const DAQ::Location&, const Image&)           throw(Exception);
  Source(const DSS::BranchId&, const DSS::Repository&) throw(Exception); 
public:
 ~Source() {}
public:
  const DVI::Version& release()       const; 
  const char*         platform()      const; 
  uint32_t            firmware()      const;
  uint64_t            serial_number() const;
public:  
  const RMS::InstructionList* registers() const;   
public:
  const DAQ::Location& location() const {return _location;} 
public:
  int numof_ccds() const;        
public:  
  void synopsis(int indent=0) const; 
public:
  bool eol() const {return _bucket.eol();}    
private:
  friend class Image;
  friend class Slice;
private:
  void _discard();    
private:
  const DSS::Id& _slice() const {return *_bucket.link();}                
private:
  DSS::StoredBucket _bucket; 
  DAQ::Location     _location;  
};

}

#endif

