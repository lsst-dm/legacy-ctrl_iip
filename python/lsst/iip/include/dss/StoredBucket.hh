
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
 
#ifndef DSS_STOREDBUCKET
#define DSS_STOREDBUCKET

#include "osa/FileException.hh"

#include "dss/Store.hh"
#include "dss/Id.hh"
#include "dss/PathName.hh"

namespace DSS {
  
class StoredBucket {
public:
  StoredBucket(const Id&   id, const PathName&) throw(OSA::FileException);
  StoredBucket(const char* id, const PathName&) throw(OSA::FileException);
public:
  StoredBucket(const Id&   id, const Repository&) throw(OSA::FileException);
  StoredBucket(const char* id, const Repository&) throw(OSA::FileException);  
public:
 ~StoredBucket();
public:
  operator bool() const {return id();}  
public:
  const Id& id() const {return _id;}
public:  
  const char*     name()     const; 
  const char*     content()  const;
  int             size()     const;
  const Id*       link()     const;
  const PathName& pathname() const {return _pathname;} 
public:
  bool eol() const {return !*link();}  
public:
  bool advance();   
private:  
  char*    _base;
  int      _size;  
  Id       _id;
  PathName _pathname;
};

}

#endif

