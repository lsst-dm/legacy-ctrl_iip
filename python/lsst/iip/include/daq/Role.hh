
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
 
#ifndef DAQ_ROLE
#define DAQ_ROLE

namespace DAQ {

class __attribute__((__packed__)) Role {
public:
  enum {MAX=127};
public:
  Role()                   {_value[0] = 0;} 
  Role(const char* value);  
  Role(const Role&);    
public:
  Role& operator=(const Role&);
  Role& operator=(const char*);
public:
 ~Role() {}
public:
  operator bool() const {return _value[0];} 
public:
  const char* value() const {return _value;} 
public:
  void reset() {_value[0] = 0; return;}          
protected:
  char _value[MAX + 1];     
 };

}

#endif

