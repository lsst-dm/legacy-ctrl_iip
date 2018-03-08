
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
 
#ifndef DSS_IDENTIFIER
#define DSS_IDENTIFIER

#include "dss/Id.hh"

#include <stdint.h>

namespace DSS {

class __attribute__((__packed__)) Identifier {
public: 
  Identifier(const Id& bucket, uint8_t partition, const Id& link) : _bucket(bucket), _link(link),        _partition(partition) {}
  Identifier(const Id& bucket, uint8_t partition)                 : _bucket(bucket), _link((uint64_t)0), _partition(partition) {}
public:
 ~Identifier() {}
public: 
  uint8_t   partition() const {return _partition;}
  const Id& bucket()    const {return _bucket;}
  const Id& link()      const {return _link;}
private:
  Id      _bucket;
  Id      _link;
  uint8_t _partition;
  uint8_t _pad[7];
};

}

#endif



 
 