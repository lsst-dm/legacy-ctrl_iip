
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

#ifndef IMS_IMAGEID
#define IMS_IMAGEID

#include "dss/RootId.hh"

namespace IMS {

class __attribute__((__packed__)) ImageId : public DSS::RootId {
public: 
  ImageId()                        : DSS::RootId()      {}                                    
  ImageId(const DSS::RootId clone) : DSS::RootId(clone) {}                                   
  ImageId(const ImageId& clone)    : DSS::RootId(clone) {}
public:
 ~ImageId() {} 
public:  
  ImageId& operator=(const ImageId& clone) {DSS::RootId::operator=(clone); return *this;}
 };

}


#endif

