
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
 
#ifndef IMS_SCIENCE
#define IMS_SCIENCE

#include "ims/Stripe.hh"
#include "ims/Slice.hh"

namespace IMS {
 
class Science : public Slice {
public:
  Science(const Source& source) : Slice(source) {}
public:
 ~Science() {}
public:
 const char *data(void) {return _data();}
 int         size(void) {return _size();} 
 void decode0(  Stripe* ccd0);
 void decode1(  Stripe* ccd1); 
 void decode2(  Stripe* ccd2); 
 void decode01( Stripe* ccd0, Stripe* ccd1); 
 void decode02( Stripe* ccd0, Stripe* ccd2); 
 void decode12( Stripe* ccd1, Stripe* ccd2); 
 void decode13( Stripe* ccd1, Stripe* ccd3); 
 void decode012(Stripe* ccd0, Stripe* ccd1, Stripe* ccd2); 
};

}

#endif

