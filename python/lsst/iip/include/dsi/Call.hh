
/*
**  Package:
**	
**
**  Abstract:
**      
**
** ONLY when member function wait() returns true is input pointed to by arguments valid.
** In such a case its "error" argument returns the status response from any one server 
** called. These values are either one of the following four enumerations:
**  - NONE if the call to the server was succesfull.
**  - TIMOUT if a response from the server was not received.
**  - NOT_A_REPONSE if the response was not a valid server response
**  - DUPLICATE if the response had previously been returned. 
**  Or a server specific value. However, independent of returned value a zero (0) value 
**  ALWAYS indicates SUCCESS. 
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
 
#ifndef DSI_CALL
#define DSI_CALL

#include "dsi/Socket.hh"
#include "dsi/Address.hh"
#include "dsi/Frame.hh"

namespace DSI {

class Call : public Frame {
public:
  static const char* decode(int error, char* buffer) {return Frame::decode(error, buffer);}
public:
  enum Function : uint8_t {F0, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15, F16, F17, F18, F19, F20, F21, F22, F23, F24, F25, F26, F27, F28, F29, F30, F31};
protected:
  Call(enum Function, Socket&);
  Call(enum Function, Socket&, const Address*);
protected: 
  Call(enum Function, const void* payload, int sizeof_payload, Socket&);
  Call(enum Function, const void* payload, int sizeof_payload, Socket&, const Address*);
protected: 
  Call(enum Function, const void* header, int sizeof_header, const void* payload, int sizeof_payload, Socket&);
  Call(enum Function, const void* header, int sizeof_header, const void* payload, int sizeof_payload, Socket&, const Address*); 
protected: 
  Call(enum Function, int output_sizeof, Socket&);
  Call(enum Function, int output_sizeof, Socket&, const Address*); 
protected: 
  Call(enum Function, const void* payload, int sizeof_payload, int output_sizeof, Socket&);
  Call(enum Function, const void* payload, int sizeof_payload, int output_sizeof, Socket&, const Address*);    
public:
 ~Call() {}
public:
  const Set&  accept() const {return _frame.accept;}   
protected: 
  bool wait(              int& error); 
  bool wait(void* output, int& error);
protected: 
  bool wait(              int& error, uint8_t& source); 
  bool wait(void* output, int& error, uint8_t& source);  
private:
  Socket&  _socket;
  unsigned _remaining;
  Frame    _frame;
  };
 
}

#endif

