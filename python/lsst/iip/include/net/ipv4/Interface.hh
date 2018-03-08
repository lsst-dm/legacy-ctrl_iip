
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
 
#ifndef IPV4_INTERFACE
#define IPV4_INTERFACE

#include <stdint.h>

#include "linked/Element.hh"
#include "net/ipv4/Flags.hh"

namespace IPV4 {

class Interface : public Linked::Element {
public:
  Interface() {}
public:
  Interface(const char* name, unsigned type, void* interface) : Linked::Element(), _name(name), _type(type) {_interface[type] = interface; _interface[type ^ 1] = (void*)0;}
public:   
  Interface(const Interface& clone) : Linked::Element() {_name = clone._name; _type = clone._type; _interface[0] = clone._interface[0]; _interface[1] = clone._interface[1];}     
public:
  Interface& operator=(const Interface& clone)          {_name = clone._name;  _type = clone._type;  _interface[0] = clone._interface[0];  _interface[1] = clone._interface[1];  return *this;} 
  Interface& operator=(Interface* clone)                {_name = clone->_name; _type = clone->_type; _interface[0] = clone->_interface[0]; _interface[1] = clone->_interface[1]; return *this;}  
public:  
 ~Interface() {}
public: 
  const char* name()    const; 
  uint32_t    address() const;
  uint32_t    bcst()    const;
  uint32_t    mask()    const;                             
  uint32_t    subnet()  const {return mask() & address();}    
  unsigned    flags()   const;
public:
   unsigned mtu(int) const;           
   unsigned mtu()    const; 
public:
   const uint8_t* link() const;          
public:
  Interface* forward() {return (Interface*)Linked::Element::flink();} 
  Interface* reverse() {return (Interface*)Linked::Element::blink();}     
public: 
  bool match(                    unsigned accepts=Flags::ALL, unsigned rejects=Flags::NONE);
  bool match(const char* filter, unsigned accepts=Flags::ALL, unsigned rejects=Flags::NONE);
  bool match(uint32_t    filter, int accepts=Flags::ALL, int rejects=Flags::NONE);
 public: 
  bool within(uint32_t base, uint32_t prefix) const;                                                   
public:
  void print(int indent=0) const; 
private:
  friend class Interfaces;
private:
  enum {IPV4=0, LINK=1};   
private:
  bool _fold(const Interface*);            
private:
  const char* _name;
  unsigned    _type;
  void*       _interface[2];
  };
 
}

#endif

