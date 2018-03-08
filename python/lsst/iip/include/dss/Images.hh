
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
 
#ifndef DSS_IMAGES
#define DSS_IMAGES

#include "dss/Store.hh"
#include "dss/Repository.hh"
#include "osa/Folder.hh"

namespace DSS {

class Images {
public:
  Images(const char* repository, const char* partition);
public:  
  Images(const Store&);                 
public:
 ~Images() {}
public:
  const char* id();   
public:
  const Repository& repository() const {return _repository;}     
private:
  Repository  _repository;
  OSA::Folder _folder; 
  };

}

#endif


 
 