
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
 
#ifndef DAQ_INTERFACE
#define DAQ_INTERFACE

#include <stdint.h>

namespace DAQ {

class __attribute__((__packed__)) Interface {
public:
  enum {UNDEFINED=128};
public:
 enum Number {A=0, B=1, C=2};
public: 
  Interface()                       {_interface[A] = UNDEFINED;           _interface[B] = UNDEFINED;           _interface[C] = UNDEFINED;}
  Interface(const Interface& clone) {_interface[A] = clone._interface[A]; _interface[B] = clone._interface[B]; _interface[C] = clone._interface[C];}
public:
 ~Interface() {} 
public: 
  Interface& operator=(const Interface& clone) {_interface[A] = clone._interface[A]; _interface[B] = clone._interface[B]; _interface[C] = clone._interface[C]; return*this;}
public:
  uint8_t lookup(enum Number interface) const {return _interface[interface];}
public:   
  const char* presentation(char* buffer) const; 
public:
  void print(int indent=0) const;
public:
  void insert(enum Number interface, uint8_t value) {_interface[interface] = value;} 
public:  
  void reset() {_interface[A] = UNDEFINED; _interface[B] = UNDEFINED; _interface[C] = UNDEFINED;}
protected:
 uint8_t _interface[4];  
 };
 
}

#endif

