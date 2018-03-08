
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
 
#ifndef DAQ_PATH
#define DAQ_PATH

namespace DAQ {

class __attribute__((__packed__)) Path {
public:
  enum {MAX=127};
public:
  Path()                   {_value[0] = 0;} 
  Path(const char* value);  
  Path(const Path&);    
public:
  Path& operator=(const Path&);
  Path& operator=(const char*);
public:
 ~Path() {}
public: 
  int lane() const; 
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

