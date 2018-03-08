
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
 
#ifndef DAQ_PARTITION
#define DAQ_PARTITION

namespace DAQ {

class __attribute__((__packed__)) Partition {
public:
  enum {MAX=127};
public:
  Partition()                   {_value[0] = 0;} 
  Partition(const char* value);  
  Partition(const Partition&);    
public:
  Partition& operator=(const Partition&);
  Partition& operator=(const char*);
public:
 ~Partition() {}
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

