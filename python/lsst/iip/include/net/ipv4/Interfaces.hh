
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
 
#ifndef IPV4_INTERFACES
#define IPV4_INTERFACES

#include "linked/List.hh"
#include "net/ipv4/Flags.hh"
#include "net/ipv4/Interface.hh"

namespace IPV4 {

class Interfaces {
public:
  enum {MAX= 64};
public:
  Interfaces(                    unsigned accepts=Flags::ALL, unsigned rejects=Flags::NONE);
  Interfaces(const char* filter, unsigned accepts=Flags::ALL, unsigned rejects=Flags::NONE);
public:  
 ~Interfaces();
public: 
  Interface* head() {return (Interface*)_list.head();}
  Interface* tail() {return (Interface*)_list.tail();}
  Interface* eol()  {return (Interface*)_list.last();}
public:
   Interface* match(const char* filter, unsigned accepts=Flags::ALL, unsigned rejects=Flags::NONE); 
public:   
  Interface* contains(uint32_t base, uint32_t prefix); 
public:
  int numof();    
public:
  void print(int indent=0); 
private:
  void* _preload();  
private:
  Linked::List _list;
  void*        _interfaces;
  char         _freelist[MAX * sizeof(Interface)];
  };
 
}

#endif

