
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
 
#ifndef DSI_SET
#define DSI_SET

#include <stdint.h>

namespace DSI {

class __attribute__((__packed__)) Set {
public:
  enum {SIZE=128};
public:
  Set();
public:  
  Set(uint8_t index);
  Set(uint8_t base, unsigned span);
public:  
  Set(const Set&); 
  Set(const Set&, const Set&);    
public:
 ~Set() {} 
public:                               
  Set& operator =(const Set&);                
  Set& operator|=(const Set&);                     
  Set& operator&=(const Set&);
  Set& operator^=(const Set&);                                                                           
public:
  Set operator&(const Set& operand) {Set mask = operand; mask &= *this; return mask;}
  Set operator|(const Set& operand) {Set add  = operand; add  |= *this; return add;}
  Set operator^(const Set& operand) {Set diff = operand; diff ^= *this; return diff;}
  Set& operator~();
public:
  operator bool() const {return _set[3] | _set[2] | _set[1] | _set[0];} 
public:
  unsigned numof() const;                  
public:
  bool has(uint8_t index) const;
public:  
  bool had(uint8_t index);
public:  
  uint8_t remove();
public:
  void insert(uint8_t index);
public:
  void empty(); 
public:
  void print(int offset=0) const;   
private:
  uint32_t _set[4];
 };

}

#endif

