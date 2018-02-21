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
 
#ifndef ARP_BARRIER
#define ARP_BARRIER

namespace ARP  {

class Barrier {
public:
  Barrier() {}
  Barrier(uint32_t name); 
public:
 ~Barrier();
public:
  uint32_t name() {return _name;}  
public:
  void block(unsigned timeout);
  void lower();
private:
  uint32_t _name;
  unsigned _barrier; 
};

}

#endif
