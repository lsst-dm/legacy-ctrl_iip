
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
 
#ifndef RMS_REGREQUEST
#define RMS_REGREQUEST

#include "dsi/Call.hh"
#include "dsi/Address.hh"

namespace RMS {

class InstructionList;  
class Client;

class RegRequest : public DSI::Call {
public:
  RegRequest(const InstructionList&, Client&);
  RegRequest(const InstructionList&, Client&, const DSI::Address&);
  
public: 
  bool wait(InstructionList*, int& error, uint8_t& source);
  
public:
  ~RegRequest() {}
};
 
}

#endif

