
/*
**  Package:
**	
**
**  Abstract:
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
 
#ifndef DSS_PARTITION
#define DSS_PARTITION

#include "linked/List.hh"

#include "dss/Exception.hh"
#include "dss/Id.hh"
#include "dss/PathName.hh"
#include "dss/Bucket.hh"
#include "dss/Page.hh"
#include "dss/Summary.hh"
#include "dss/Stats.hh"
#include "dss/Id.hh"
#include "dss/Catalog.hh"

namespace DSS {

class Partition {
public:
  Partition(const char* repository, const char* partition, unsigned id=0); 
public:  
 ~Partition();
public:
  int32_t lookup(const char* name, void* buffer);
  int32_t remove(const char* name);
public:
  int32_t open(const char* name, const Id& link, void* buffer);
  int32_t open(const Id&   name, const Id& link, void* buffer);
public:  
  void write(const Page*, int length); 
  int  close(const Summary*, void* output);
public:
  int sample(void* buffer);
public:
  unsigned id() const {return _id;}  
public:   
  int reset() {_stats.reset(); return 0;}
public:
  const char* repository() {return _pathname.value();}       
private:
  Bucket* _lookup(const Id&); 
private:
  unsigned _numof();  
private:
  PathName     _pathname;
  int          _error;
  Catalog      _catalog;
  Linked::List _pending;
  unsigned     _id;
  Stats        _stats;
  }; 

}

#endif

