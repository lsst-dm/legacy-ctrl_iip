
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
 
#ifndef OSA_TIMESTAMP
#define OSA_TIMESTAMP

#include <stdint.h>
#include <time.h>

namespace OSA {

class __attribute__((__packed__)) TimeStamp { 
public:
 TimeStamp(); 
 TimeStamp(time_t);        
 TimeStamp(const TimeStamp& clone) : _timestamp(clone._timestamp) {} 
public:
 ~TimeStamp() {}
public:  
  TimeStamp& operator=(const TimeStamp& clone) {_timestamp  = clone._timestamp; return *this;} 
public:  
  const char* string() const;
public:
   operator uint64_t() const;    
private:   
 uint64_t _timestamp;
 };

}

#endif

