
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
 
#ifndef DSI_SERVER
#define DSI_SERVER

#include "net/ipv4/Address.hh"
#include "net/ipv4/Socket.hh"
#include "net/ipv4/Interface.hh"

#include "dsi/Task.hh"
#include "dsi/Interface.hh"
#include "dsi/Exception.hh"
#include "dsi/Call.hh"

namespace DSI {

class Server {
protected:
  Server(const char* service, const char* partition, const Set&)                                              throw (Exception); 
  Server(const char* service, const char* partition, const Set&, const char* interface)                       throw (Exception); 
  Server(const char* service, const char* partition, const Set&, const char* interface, const IPV4::Address&) throw (Exception);    
public:
 ~Server() {delete _socket;}
public:
  uint8_t pid() {return _pid;} 
public:
  const IPV4::Address& address() const {return _socket->address;}
public: 
  enum Call::Function start();  
protected:
  Set& accepts() {return _cache.accepts();}      
protected:
  virtual void M00(Task* task) {delete task;}
  virtual void M01(Task* task) {delete task;}
  virtual void M02(Task* task) {delete task;}
  virtual void M03(Task* task) {delete task;}
  virtual void M04(Task* task) {delete task;}
  virtual void M05(Task* task) {delete task;}
  virtual void M06(Task* task) {delete task;}
  virtual void M07(Task* task) {delete task;} 
  virtual void M08(Task* task) {delete task;}
  virtual void M09(Task* task) {delete task;}
  virtual void M10(Task* task) {delete task;}
  virtual void M11(Task* task) {delete task;}
  virtual void M12(Task* task) {delete task;}
  virtual void M13(Task* task) {delete task;}
  virtual void M14(Task* task) {delete task;}
  virtual void M15(Task* task) {delete task;} 
  virtual void M16(Task* task) {delete task;}
  virtual void M17(Task* task) {delete task;}
  virtual void M18(Task* task) {delete task;}
  virtual void M19(Task* task) {delete task;}
  virtual void M20(Task* task) {delete task;}
  virtual void M21(Task* task) {delete task;}
  virtual void M22(Task* task) {delete task;}
  virtual void M23(Task* task) {delete task;} 
  virtual void M24(Task* task) {delete task;}
  virtual void M25(Task* task) {delete task;}
  virtual void M26(Task* task) {delete task;}
  virtual void M27(Task* task) {delete task;}
  virtual void M28(Task* task) {delete task;}
  virtual void M29(Task* task) {delete task;}
  virtual void M30(Task* task) {delete task;}
  virtual void M31(Task* task) {delete task;}      
protected:
  void stop(   enum Call::Function function)     {_stop    |= 1 << function; return;}
  void respond(enum Call::Function function)     {_respond |= 1 << function; return;}
  void respondStop(enum Call::Function function) {respond(function); stop(function); return;}
private:
  typedef void (Server::* Method)(Task*);       
private:
  void _call(unsigned function, Task* task) {Method method = _lut[function]; (this->*method)(task); return;} 
private:
  void _construct_lut();
private:
  enum {MAX_FUNCTIONS = 32}; 
private:
  unsigned      _stop;
  unsigned      _respond;
  unsigned      _pid;
  Interface     _cache;
  IPV4::Socket* _socket;
  FreeList      _freelist;
private:  
  Method _lut[MAX_FUNCTIONS];
  }; 
                 
}

#endif

