
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
 
#ifndef DSI_FRAME
#define DSI_FRAME

#include <stdint.h>

#include "net/ipv4/Address.hh"

#include "dsi/Set.hh"
#include "dsi/Address.hh"
#include "net/Endian.hh"

namespace DSI {

class __attribute__((__packed__)) Frame {
public:
  enum : int32_t {NONE = 0, TIMOUT=-1, INVALID_RESPONSE=-2,  DUPLICATE=-3, INVALID_REQUEST=-4, NOSUCH_INTERFACE=-5, NOSUCH_PARTITION=-6, NOSUCH_SERVICE=-7};
public:
  static const char* decode(int error);
  static const char* decode(int error, char* buffer);  
public:
  Frame(); 
public:  
  Frame(uint8_t function,                         uint32_t sequence, const IPV4::Address&, const Set&);
  Frame(uint8_t function, uint16_t output_sizeof, uint32_t sequence, const IPV4::Address&, const Set&);
public:  
  Frame(uint8_t function,                         uint32_t sequence, const IPV4::Address&);
  Frame(uint8_t function, uint16_t output_sizeof, uint32_t sequence, const IPV4::Address&);  
public:  
  Frame(const Frame&);
public:
 ~Frame() {} 
public:
  bool valid() const {return  Net::Endian::local(_magic) == MAGIC;}
  bool valid(const Frame* request) const;  
 public:
  uint8_t requester() const {return _requester;} 
public: 
  unsigned magic()         const {return  Net::Endian::local(_magic);}
  unsigned function()      const {return _function;} 
  unsigned sequence()      const {return Net::Endian::local(_sequence);}
  unsigned status()        const {return Net::Endian::local(_status);}
  int      sizeof_output() const {return Net::Endian::local(_sizeof_output);}
public: 
  void set(uint32_t status)  {_status = Net::Endian::wire(status);}
  void shut()                {_function = 32;} 
public:
  void remove() {_requester = accept.remove();} 
public:
  void dump();   
private:
  enum {MAGIC = 0xABBABABE};    
private:
  uint32_t _magic; 
  uint32_t _sequence;
  int32_t  _status;
  uint8_t  _requester;
  uint8_t  _function;
  uint16_t _sizeof_output;
public: 
  IPV4::Address source;
  Set           accept;
  };

}

#endif

