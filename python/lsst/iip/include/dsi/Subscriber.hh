
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
 
#ifndef DSI_SUBSCRIBER
#define DSI_SUBSCRIBER

#include "net/ipv4/Address.hh"
#include "net/ipv4/Socket.hh"

#include "dsi/Interface.hh"
#include "dsi/Frame.hh"
#include "dsi/Call.hh"
#include "dsi/Set.hh"
#include "dsi/Address.hh"
#include "dsi/Exception.hh"
#include "dsi/Symbol.hh"

namespace DSI {

class Subscriber {
protected: 
  Subscriber(const char* service, const char* partition, const Set&) throw (Exception);                               
public:
 ~Subscriber();
public:
  const char* partition() const {return _partition.name;}  
public:
  Address service; 
public:
  const IPV4::Address& address() const {return _socket->address;}
protected: 
  enum Call::Function _block(const Set&);
protected:
  virtual bool M00(const void*, int) {return false;}
  virtual bool M01(const void*, int) {return false;}
  virtual bool M02(const void*, int) {return false;}
  virtual bool M03(const void*, int) {return false;}
  virtual bool M04(const void*, int) {return false;}
  virtual bool M05(const void*, int) {return false;}
  virtual bool M06(const void*, int) {return false;}
  virtual bool M07(const void*, int) {return false;} 
  virtual bool M08(const void*, int) {return false;}
  virtual bool M09(const void*, int) {return false;}
  virtual bool M10(const void*, int) {return false;}
  virtual bool M11(const void*, int) {return false;}
  virtual bool M12(const void*, int) {return false;}
  virtual bool M13(const void*, int) {return false;}
  virtual bool M14(const void*, int) {return false;}
  virtual bool M15(const void*, int) {return false;} 
  virtual bool M16(const void*, int) {return false;}
  virtual bool M17(const void*, int) {return false;}
  virtual bool M18(const void*, int) {return false;}
  virtual bool M19(const void*, int) {return false;}
  virtual bool M20(const void*, int) {return false;}
  virtual bool M21(const void*, int) {return false;}
  virtual bool M22(const void*, int) {return false;}
  virtual bool M23(const void*, int) {return false;} 
  virtual bool M24(const void*, int) {return false;}
  virtual bool M25(const void*, int) {return false;}
  virtual bool M26(const void*, int) {return false;}
  virtual bool M27(const void*, int) {return false;}
  virtual bool M28(const void*, int) {return false;}
  virtual bool M29(const void*, int) {return false;}
  virtual bool M30(const void*, int) {return false;}
  virtual bool M31(const void*, int) {return false;}      
private:
  typedef bool (Subscriber::* Method)(const void* publication, int sizeof_publication);       
private:
  bool _call(unsigned function, const void* publication, int sizeof_publication) {Method method = _lut[function]; return (this->*method)(publication, sizeof_publication);}
private:   
  void _construct_lut();
  int  _wait(Frame* frame);
private:
  unsigned      _pid;
  IPV4::Socket* _socket;
  char*         _input; 
  Interface     _cache;
  Symbol        _partition;
private:
  enum {MAX_FUNCTIONS = 32};    
  Method _lut[MAX_FUNCTIONS];
  };  
 
}

#endif

