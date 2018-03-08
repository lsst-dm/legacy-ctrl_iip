
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
 
#ifndef DSI_SYMBOL
#define DSI_SYMBOL

#include <stdint.h>

namespace DSI {

class __attribute__((__packed__)) Symbol {
public:
  enum {MAX=63};
public:  
  Symbol() {name[0] = 0;}
public:   
  Symbol(const char* name);
  Symbol(const Symbol&); 
public:
  Symbol& operator=(const Symbol&);  
public:
 ~Symbol() {}
public:
  char name[MAX + 1];             
public:
  operator bool() const {return name[0];} 
public:
  void invalidate() {name[0] = 0;}        
 };

}


#endif

