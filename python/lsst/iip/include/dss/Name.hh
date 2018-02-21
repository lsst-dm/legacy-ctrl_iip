
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
 
#ifndef DSS_NAME
#define DSS_NAME

#include "dss/Id.hh"
#include "dss/Store.hh"

#include <stdint.h>

namespace DSS {

class __attribute__((__packed__)) Name {
public:
  enum {MAX=64};
public: 
  Name(const char* bucket, const Id& link, uint8_t partition=0);
  Name(const char* bucket,                 uint8_t partition=0);
public:
  Name(const char* bucket, const Id& link, const Store&);
  Name(const char* bucket,                 const Store&);  
public:
 ~Name() {}
public: 
  uint8_t     partition() const {return _partition;}
  const char* bucket()    const {return _bucket;}
  const Id&   link()      const {return _link;}
private:
  Id      _link;
  uint8_t _partition;
  uint8_t _pad[7];
  char    _bucket[MAX];
};

}

#endif



 
 