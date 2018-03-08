
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
 
#ifndef IMS_WAVEFRONT
#define IMS_WAVEFRONT

#include "ims/Stripe.hh"
#include "ims/Slice.hh"

namespace IMS {
 
class WaveFront : public Slice {
public:
  WaveFront(const Source& source) : Slice(source) {}
public:
 ~WaveFront() {}
public:
 void decode(Stripe* ccd);
};

}

#endif

