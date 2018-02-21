
/*
**  Package:
**	
**
**  Abstract:
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
 
#ifndef DSI_FREELIST
#define DSI_FREELIST

namespace DSI {

class FreeList {
public:
  enum {ONE_BLOCK      = 1024*64};          // Maximum size of a network operation (must be a power of two)            
  enum {ONE_ALLOCATION = ONE_BLOCK * 2}; // size (in bytes) of a single allocation
  enum {MAX_PENDING    = 64};            // Freelist size (in units of ALLOCATION)
public:
  FreeList(int max_size = MAX_PENDING);
public:  
 ~FreeList();
public:
  void* allocate(); 
  void  deallocate(void*); 
private:
  void* _rset;
  void* _pool;
  };

}

#endif

