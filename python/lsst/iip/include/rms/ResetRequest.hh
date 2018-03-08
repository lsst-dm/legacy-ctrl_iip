 
#ifndef RMS_RESETREQUEST
#define RMS_RESETREQUEST

#include "dsi/Call.hh"
#include "dsi/Address.hh"

namespace RMS {

class Client;
  
class ResetRequest : public DSI::Call
{
public:
  enum {FE_RESET=0, UNDEF_RESET=1};
public:
  ResetRequest(const unsigned& reset, Client&);
  ResetRequest(const unsigned& reset, Client&, const DSI::Address&);

public: 
  bool wait(int& error, uint8_t& source);
public:
  ~ResetRequest() {}
};
  
}

#endif

