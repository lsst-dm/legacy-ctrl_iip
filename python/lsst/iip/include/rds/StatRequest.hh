 
#ifndef RDS_STATREQUEST
#define RDS_STATREQUEST

#include "dsi/Call.hh"
#include "dsi/Address.hh"

namespace RDS {

class Client;
class Stats;
  
class StatRequest : public DSI::Call {
public:
  StatRequest(const bool& reset, Client&);
  StatRequest(const bool& reset, Client&, const DSI::Address&);

public: 
  bool wait(Stats*, int& error, uint8_t& source);
public:
  ~StatRequest() {}
};
  
}

#endif

