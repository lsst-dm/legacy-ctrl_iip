
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
 
#ifndef DSS_CACHE
#define DSS_CACHE

#include "dsi/Address.hh"
#include "dsi/Client.hh"
#include "dss/Summary.hh"
#include "dss/Stats.hh"

namespace DSS {

class Cache : public DSI::Client {
public:
  enum {PAGE_SIZE2 = 15}; // expressed as factor of 2 (32 KBytes)...
public:                         
  Cache(const char* partition);     
public:
 virtual ~Cache() {} 
public:
  void fill(uint64_t bucket, uint32_t page, const void* content, int sizeof_content);
public:  
  const Summary* close(const Summary*);
public:
  const Stats* read(Stats* buffer);
public:
  int reset();  
private:
  DSI::Address _server; // Single-cast address of server... 
  Summary      _summary;  
  };

}

#endif

