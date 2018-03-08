
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
 
#ifndef IMS_IMAGE
#define IMS_IMAGE

#include "ims/Store.hh"
#include "ims/Images.hh"
#include "ims/Exception.hh"

#include "dss/Repository.hh"
#include "dss/RootId.hh"
#include "dss/StoredBucket.hh"
#include "daq/Location.hh"
#include "daq/LocationSet.hh"
#include "osa/TimeStamp.hh"
#include "dvi/Version.hh"

namespace IMS {
  
class Image {
public:
  static void header();          
public:
  Image(const char* name, Store&)                      throw(Exception); 
  Image(const char* id, Images&)                       throw(Exception);
public:  
  Image(const DSS::RootId& id, const DSS::Repository&) throw(Exception);
public:
 ~Image() {}
public:
  const char* name() const {return _bucket.name();} 
public:
  const OSA::TimeStamp&   creation() const; 
  const DVI::Version&     release()  const;         
  const DAQ::LocationSet& sources()  const;
public: 
  void synopsis() const; 
public:
  void remove(Store&); 
public:
  const DSS::RootId& id() const {return _id;}               
private:
  friend class Source;
private:
  DSS::RootId       _id;      
  DSS::StoredBucket _bucket; 
};

}

#endif

