
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
 
#ifndef INIT_DIRECTORY
#define INIT_DIRECTORY

namespace INIT {

class __attribute__((__packed__)) Directory {
public:
  enum {MAX=127};
public:
  Directory()                   {_value[0] = 0;} 
  Directory(const char* value);  
  Directory(const Directory&);    
public:
  Directory& operator=(const Directory&);
  Directory& operator=(const char*);
public:
 ~Directory() {}
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

