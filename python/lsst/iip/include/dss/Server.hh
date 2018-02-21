
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
 
#ifndef DSS_SERVER
#define DSS_SERVER

#include "dss/Attributes.hh"

#include "dsi/Exception.hh"
#include "dsi/Task.hh"
#include "dsi/SymbolTable.hh"
#include "dsi/Server.hh"
 
#include "dss/Partition.hh"

namespace DSS {

class Server : public DSI::Server {
public:
  Server(const char* interface, const char* repository) throw (DSI::Exception); 
public:  
  virtual ~Server();
public:
  void M00(DSI::Task*); // Return own attributes...
  void M02(DSI::Task*); // Lookup bucket identifier...
  void M03(DSI::Task*); // Remove bucket identifier...  
public:   
  void M04(DSI::Task*); // Open  per partition bucket...
  void M05(DSI::Task*); // Write per partition bucket pages...
  void M06(DSI::Task*); // Close per partition bucket...
  void M07(DSI::Task*); // Create per partition bucket...
public: 
  void M08(DSI::Task*); // Sample per partition statistics... 
  void M09(DSI::Task*); // Reset  per partition statistics...
public:
  void M30(DSI::Task*); // Restart DSS server... 
  void M31(DSI::Task*); // Shutdown DSS server... 
private:
  Partition* _allocate(const DSI::Symbol*);
  Partition* _lookup(unsigned id);    
private:
  DSI::SymbolTable _table;
  Attributes       _attributes;
  Partition*       _partition[DSI::SymbolTable::MAX + 1];
  }; 

}

#endif

