
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
 
#ifndef DSS_SUMMARY
#define DSS_SUMMARY

#include "dsi/Set.hh"
#include "dss/Pid.hh"
#include "dss/Page.hh"
#include "dss/Id.hh"

namespace DSS {

class __attribute__((__packed__)) Summary : public DSI::Set {
public:
  Summary(                                       uint8_t partition=0) : DSI::Set(),    _bucket(),       _partition(partition) {} 
  Summary(const Id& bucket,                      uint8_t partition=0) : DSI::Set(),    _bucket(bucket), _partition(partition) {}
  Summary(const Id& bucket, const DSI::Set& set, uint8_t partition=0) : DSI::Set(set), _bucket(bucket), _partition(partition) {}
public:
 ~Summary() {}
public: 
  Summary& operator=(const Page& clone) {_bucket = clone._bucket; return *this;}  
public:
  uint8_t   partition() const {return _partition.value();} 
  const Id& bucket()    const {return _bucket;} 
private:
  Id  _bucket;
  Pid _partition;    
  };
  
}

#endif

