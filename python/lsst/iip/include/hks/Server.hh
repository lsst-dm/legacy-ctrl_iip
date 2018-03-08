
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
 
#ifndef HKS_SERVER
#define HKS_SERVER

#include "dsi/Location.hh"
#include "dsi/Task.hh"
#include "dsi/Server.hh"

#include "daq/Preferences.hh"

namespace HKS {

class Server : public DSI::Server {
public:
  Server(const DSI::Location&, const char* interface); 
public:  
  virtual ~Server() {};
public:
  void M00(DSI::Task*); // Lookup release path + version 
  void M01(DSI::Task*); // Assign release path
  void M02(DSI::Task*); // Reset  release path
public:
  void M04(DSI::Task*); // Lookup mount-point 
  void M05(DSI::Task*); // Assign mount-point
  void M06(DSI::Task*); // Reset  mount-point
public:
  void M08(DSI::Task*); // Lookup role 
  void M09(DSI::Task*); // Assign role
  void M10(DSI::Task*); // Reset  role 
public:
  void M12(DSI::Task*); // Lookup source 
  void M13(DSI::Task*); // Assign source
  void M14(DSI::Task*); // Reset  source  
public:
  void M16(DSI::Task*); // Lookup interface 
  void M17(DSI::Task*); // Assign interfaces
  void M18(DSI::Task*); // Reset  interfaces  
public:
  void M31(DSI::Task*); // shutdown server
private:
  DAQ::Preferences* _preferences;
  }; 

}

#endif

