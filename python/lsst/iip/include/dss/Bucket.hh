
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
 
#ifndef DSS_BUCKET
#define DSS_BUCKET

#include <stdint.h>

#include "dss/PathName.hh"
#include "dss/Id.hh"

#include "osa/File.hh"
#include "osa/FileException.hh"
#include "dsi/Set.hh"
#include "linked/Element.hh"

namespace DSS {

class Bucket : public Linked::Element {
public:
  enum {PAGE_SIZE2 = 15};
  enum {PAGE_SIZE  = 1 << PAGE_SIZE2};
  enum {BASE=256}; 
public:
  Bucket(const char* pathname, const Id& bucket, const Id& link)                   throw(OSA::FileException);
  Bucket(const char* pathname, const Id& bucket, const Id& link, const char* name) throw(OSA::FileException);
public:
 ~Bucket() {}
public: 
  DSI::Set pending;
public:
  Id id; 
public:
  operator bool() const {return _file;}   
public:   
  int commit(const void* buffer, unsigned length, unsigned page=0);
private:
  OSA::File _file;  
  };

}

#endif

