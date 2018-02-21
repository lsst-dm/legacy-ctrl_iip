/*
** ++
**  Package:
**	
**
**  Abstract:
**
**   This class provides an interface to the ARM Performance Monitor (PM). In fact,it is 
**   simply a class wrapper to the more high-level functions of the "c" based utilities 
**   implemented by JJ Russell which provides a software interface to the ARM's hardware PM.
**   That set of functions is called the PM Utility (or PMU). The PMU is incredibly rich 
**   and this interface only exposes a small fraction of that richness. Please consult the
**   PMU header files for a more complete description of their function.
**
**  This single class allows the monitoring and storing of six (6) different monitors. 
**  Each monitor is identified by a small integer and the set of allowed values are found in  
** "ARM® Cortex®-A9 Revision: r4p1 Technical Reference Manual" Chapter 11, starting on
**  page 11-167. 
** 
**  The constructor for this class takes six (6) arguments, each argument corresponding to
**  one of the six monitors described above. Once this class is instantiated monitoring is 
**  initiated by calling its "start" member and terminated by calling its "stop" member. 
**  The results are may at any point in time by dumped to standard output by calling its 
**  "dump" member.  In short, one measures a piece of code to be monitored by bracketing 
**  that code with a "start" and "stop". For example, the enumerations for the following
**  monitors are:
**
**   1 - Instruction cache miss
**   2 - Instruction Micro TLB miss
**   3 - Data cache miss
**   4 - Data cache access
**   6 - Data Reads
**   7 - Data Writes
**
**  Therefore, to monitor these six counters for a routine called "myTestCode()" and dump
**  their results:
**
**  PMU::Monitor monitor(7, 1, 2, 3, 4, 6); // The order does not matter...
**
**    monitor.start();
**    myTestCode();
**    monitor.stop();
**
**    monitor.dump();
**
** The class will store the results for up to Monitor::MAX (64) iterations. For example, 
** to repeat the above measurement twelve (12) times: 
**
**  PMU::Monitor monitor(7, 1, 2, 3, 4, 6); // The order does not matter...
**
**  int remaining = 12;
**
**  do { monitor.start(); myTestCode(); monitor.stop();} while(--remaining);
**
**  monitor.dump();
**
**   Experience has shown the start and stop overhead is ~19 clock cycles. Note that cycles 
**   are measured in CPU tics. I., e., for an 800 MHZ processor one clock tic is 1.25 NS.
**   Beware the optimizer reordering your code. 
**   The "restart" member is used if the iteration pointer  is not to be advanced and the
**   "reset" member resets the iteration pointer.
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
 
#ifndef PMU_MONITOR
#define PMU_MONITOR

#include "pmu/pmu.h"

namespace PMU {

class Monitor {
public:
  enum {MAX=64};
public: 
  Monitor(int, int, int, int, int, int); 
public:
 ~Monitor() {pmu_stop();} 
public:
  void start()   {pmu_reset(); pmu_start();}
  void restart() {pmu_start();}
  void stop()    {pmu_stop(); pmu_read(&_results[_next++]);} 
  void reset()   {_next = 0;}
public: 
  void dump();
private:
  PmuResults _results[MAX]; 
  unsigned   _next;
  unsigned   _counters[6];
};

}

#endif











