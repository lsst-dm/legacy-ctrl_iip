
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
 
#ifndef IMS_GUIDING
#define IMS_GUIDING

#include "ims/Stripe.hh"
#include "ims/Slice.hh"

namespace IMS {
 
class Guiding : public Slice {
public:
  Guiding(const Source& source) : Slice(source) {}
public:
 ~Guiding() {}
public:
 void scatter01(Stripe* ccd0, Stripe* ccd1);
};

}

#endif

