
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
 
#ifndef DSI_CACHE
#define DSI_CACHE

#include "dsi/Server.hh"
#include "dsi/Task.hh"
#include "dsi/CacheCore.hh"

namespace DSI {

class Cache : public DSI::Server {
public:
  Cache(const char* interface, const char* path);
public:  
 virtual ~Cache() {}
public:
  void M00(Task*); // LOOKUP service and its members (client)
  void M01(Task*); // PROBE service (server)
public: 
  void M04(Task*); // ADD or REMOVE service members
public: 
  void M31(Task*); // Shut ourselves down... 
private:
  CacheCore _cache;
}; 

}

#endif

