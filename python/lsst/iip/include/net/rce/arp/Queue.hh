/*
** ++
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
**	000 - January 09, 2007
**
**  Revision History:
**	None.
**
** --
*/
 
#ifndef ARP_QUEUE
#define ARP_QUEUE

#include <rtems.h>

#include "net/rce/arp/Barrier.hh"

namespace ARP  {

class Queue {
public:
  Queue(unsigned name);
public:
 ~Queue();
public:
  void raise(Barrier*);
  void lower(uint32_t barrier);
private:
  rtems_id _queue; 
};

}

#endif
