
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
 
#ifndef DSS_NEWSERVER
#define DSS_NEWSERVER

#include "dss/Attributes.hh"

#include "dsi/Exception.hh"
#include "dsi/Task.hh"
#include "dsi/Server.hh"
 
#include "dss/Partition.hh"

namespace DSS {

class NewServer : public DSI::Server {
public:
  NewServer(const char* partition, const char* interface, const char* repository) throw (DSI::Exception); 
public:  
  virtual ~NewServer();
public:
  void M00(DSI::Task*); // Return own attributes...
  void M02(DSI::Task*); // Lookup bucket identifier...
  void M03(DSI::Task*); // Remove bucket identifier...  
public:   
  void M04(DSI::Task*); // Open bucket...
  void M05(DSI::Task*); // Write bucket pages...
  void M06(DSI::Task*); // Close bucket...
  void M07(DSI::Task*); // Create bucket...
public: 
  void M08(DSI::Task*); // Sample statistics... 
  void M09(DSI::Task*); // Reset  statistics...
public:
  void M30(DSI::Task*); // Restart ourself... 
  void M31(DSI::Task*); // Shutdown ourself... 
private:
  Attributes _attributes;
  Partition  _partition;
  }; 

}

#endif

