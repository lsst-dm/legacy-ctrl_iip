
/*
**  Package:
**	
**
**  Abstract:
**  
** Beware: This is and must be an exact duplicate of the class by the same name found in INIT.    
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
 
#ifndef DAQ_Mountpoint
#define DAQ_Mountpoint

namespace DAQ {

class __attribute__((__packed__)) Mountpoint {
public:
  enum {MAX=127};
public:
  Mountpoint() {_value[0] = 0;} 
  Mountpoint(const char* value);  
  Mountpoint(const Mountpoint&);    
public:
  Mountpoint& operator=(const Mountpoint&);
  Mountpoint& operator=(const char*);
public:
 ~Mountpoint() {}
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

