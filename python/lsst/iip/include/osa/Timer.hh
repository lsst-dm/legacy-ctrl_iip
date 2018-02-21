
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
 
#ifndef OSA_TIMER
#define OSA_TIMER

#include <time.h>

namespace OSA {

class Timer {
public: 
  Timer();
public:
 ~Timer() {}
public:
  void start();
public:  
  long stop();  
private:
  struct timespec _start;
  struct timespec _end;
  long            _pedestal;
  };   

}

#endif

