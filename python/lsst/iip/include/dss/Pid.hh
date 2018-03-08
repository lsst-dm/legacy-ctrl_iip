
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
 
#ifndef DSS_PID
#define DSS_PID

#include <stdint.h>

namespace DSS {

class __attribute__((__packed__)) Pid {
public:
  Pid(uint8_t pid=0)    {_pid[0] = pid;}
  Pid(const Pid& clone) {_pid[0] = clone._pid[0];}
public:
 ~Pid() {}
public:  
  Pid& operator=(const Pid& clone)  {_pid[0] = clone._pid[0]; return *this;}
  Pid& operator=(uint8_t clone)     {_pid[0] = clone;         return *this;}     
public:
  uint8_t value() const {return _pid[0];} 
private:
  uint8_t _pid[8];  
  };
  
}

#endif

