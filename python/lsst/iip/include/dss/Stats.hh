
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
 
#ifndef DSS_STATS
#define DSS_STATS

#include "dss/Store.hh"

namespace DSS {

class __attribute__((__packed__)) Stats {
public: 
  Stats();
  Stats(Store&);
  Stats(const Stats&);
public:
 ~Stats() {} 
public:
  void reset();
  void reset(Store&);
public: 
  unsigned pages_requested;   // number of page store requests
  unsigned pages_stored;      // number of page store requests satisfied
public:  
  unsigned buckets_requested_open; // number of bucket open requests
  unsigned buckets_opened;         // number of bucket open requests satisfied
public:
  unsigned buckets_requested_close; // number of bucket close requests
  unsigned buckets_closed;           // number of bucket close requests satisfied
  unsigned pending;                  // Number of buckets pending close
public:
  void print(int indent=0) const;   
  };

}

#endif

