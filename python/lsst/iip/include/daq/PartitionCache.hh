
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
 
#ifndef DAQ_PARTITIONCACHE
#define DAQ_PARTITIONCACHE

#include "daq/Partition.hh"
#include "Cache.hh"

namespace DAQ {

class PartitionCache : public Partition {
public:
  PartitionCache();                   
  PartitionCache(const PartitionCache&);      
public:
  PartitionCache& operator=(const Partition&);
  PartitionCache& operator=(const PartitionCache&);
  PartitionCache& operator=(const char*);
public:
 ~PartitionCache() {}
public: 
  const char* value() const {return *this ? Partition::value() : _fallback;} 
public:
  void reset();        
private:
  const char* _fallback;
  Cache       _cache;
 };

}

#endif

