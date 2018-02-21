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
 
#ifndef HASH_KEY
#define HASH_KEY

#include <inttypes.h>
#include <stddef.h>

namespace Hash {

uint64_t Key(const uint32_t* vector, uint32_t length, uint32_t seed);   

uint64_t Key(const char* vector, uint32_t seed);   

uint64_t Key(uint64_t parent, uint32_t child);   

}

#endif
