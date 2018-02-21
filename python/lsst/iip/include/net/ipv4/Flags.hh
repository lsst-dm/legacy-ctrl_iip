/*
** ++
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
**	000 - , 2007
**
**  Revision History:
**	None.
**
** --
*/
 
#ifndef IPV4_FLAGS
#define IPV4_FLAGS

#include <net/if.h> // Contains Interface flags...

namespace IPV4 {

class Flags {
public:
  enum {ALL=-1, NONE=0};
public:  
  Flags()                   {_flags = 0;}
  Flags(unsigned flags)     {_flags = flags;}                                 
  Flags(const Flags& clone) {_flags = clone._flags;}
public:  
  Flags& operator=(const Flags& clone) {_flags = clone._flags; return *this;} 
  Flags& operator=(unsigned flags)     {_flags = flags;        return *this;} // input is assumed network order...
public:  
  Flags& operator|=(const Flags& add)  {_flags |= add._flags;  return *this;}                     
  Flags& operator&=(const Flags& mask) {_flags &= mask._flags; return *this;}    
public:  
  Flags operator&(const Flags& operand) {Flags mask = operand; mask &= *this; return mask;}
  Flags operator|(const Flags& operand) {Flags add  = operand; add  |= *this; return add;} 
public: 
  operator unsigned() const {return _flags;}   
public:
 ~Flags() {}
public:
  unsigned flags() const {return _flags;} 
public:
  char* presentation(char* buffer) const;        
private:
  unsigned _flags;
};

}

#endif
