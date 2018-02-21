
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
 
#ifndef IMS_IMAGES
#define IMS_IMAGES

#include "dss/Images.hh"
#include "ims/Store.hh"

namespace IMS {

class Images : public DSS::Images {
public:  
  Images(const Store& store) : DSS::Images(store) {}                 
public:
 ~Images() {}
  };

}

#endif


 
 