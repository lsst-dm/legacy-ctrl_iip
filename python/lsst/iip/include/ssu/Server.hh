
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
 
#ifndef SSU_SERVER
#define SSU_SERVER

#include "dsi/Task.hh"
#include "dsi/Location.hh"
#include "dsi/Server.hh"

#include "daq/Preferences.hh"

namespace SSU {

class Server : public DSI::Server {
public:
  Server(const DSI::Location& location, const char* interface); 
public:  
  virtual ~Server() {};
public:
  void M04(DSI::Task* task);  // Lookup partition name...
  void M05(DSI::Task* task);  // Assign partition name...
  void M06(DSI::Task* task);  // Reset partition name...  
  void M08(DSI::Task* task);  // Reboot all shelves' RCEs...       
private:
  void _lookup(void* buffer);          // M04 
  void _assign(const DAQ::Partition*); // M05
  void _reset();                       // M06
  void _reboot();                      // M00
private:
  DAQ::Preferences* _preferences;    
  }; 

}

#endif

