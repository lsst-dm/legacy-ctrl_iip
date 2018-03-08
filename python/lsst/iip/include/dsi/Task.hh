
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
 
#ifndef DSI_TASK
#define DSI_TASK

#include "net/ipv4/Socket.hh"

#include "dsi/Frame.hh"
#include "dsi/Call.hh"
#include "dsi/Set.hh"
#include "dsi/FreeList.hh"

namespace DSI {

class Task {
public:
  static void* operator new(size_t, FreeList*);
  static void  operator delete(void*); 
public:
  Task(const Set&, IPV4::Socket*);
  Task(const Set&, unsigned stop, unsigned respond, IPV4::Socket*);
  Task(const Task&);
public:
 ~Task();
public:
  uint8_t requester() const {return _frame.requester();}
public:   
  bool clonable() const {return _frame.accept;}
public:
  unsigned function() const {return _frame.function();}
public: 
  bool valid(int input)             {return (sizeof_input() == input) && !sizeof_output();}       
  bool valid(int input, int output) {return (sizeof_input() == input) && (sizeof_output() == output);}      
public:
  const char* input()        const {return (const char*)&this[1];} 
  char*       scratchpad()         {return (char*)input() + maxof_input();}
  char*       output()             {return scratchpad() + maxof_scratchpad();} 
public:   
  int sizeof_input() const {return _sizeof_input;}
  int maxof_input()  const {return FreeList::ONE_BLOCK - sizeof(Task);}      
public: 
  int maxof_scratchpad() const {return sizeof(Task);} 
public:  
  int sizeof_output() const {return _frame.sizeof_output();}
  int maxof_output()  const {return FreeList::ONE_BLOCK - maxof_scratchpad();}
public: 
  void set(int32_t status)  {_frame.set(status);} 
public:
  void stop()          { _stop    |= ~(1 << _frame.function());}
  void donot_respond() { _respond &= ~(1 << _frame.function());}
public:
  bool abort() const {return _stop & (1 << _frame.function());}  
private:  
  int  _wait(); 
private:
  unsigned      _stop;
  unsigned      _respond;
  IPV4::Socket* _socket;
  int           _sizeof_input;
  Frame         _frame;
  };

}

#endif

