 
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

#ifndef RMS_CLIENT
#define RMS_CLIENT

#include "dsi/Client.hh"

#include "rms/InstructionList.hh"

namespace RMS {

class Client : public DSI::Client {
public:                         
  Client(const char* partition);     
public:
  ~Client() {} 
public:
 bool reset() {return true;}
 //bool reset(DAQ::Address&);
 //bool reset(DAQ::AddressSet&);
public:
  void restart() {return;}
  //void restart(DAQ::Address&);
public:
  void shutdown() {return;}
  //void shutdown(DAQ::Address&);      
};
  
}

#endif

