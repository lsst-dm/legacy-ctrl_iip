
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

#ifndef DSS_PATHNAME
#define DSS_PATHNAME

#include <stdint.h>
#include "dss/Repository.hh"

#include "dss/Id.hh"
 
namespace DSS {

class PathName {
public:  
  PathName();
  PathName(const Repository&);
  PathName(const Repository&, const Id&);
  PathName(const Repository&, const char* id);
public: 
  PathName(const PathName&, const Id&);
  PathName(const PathName&, const char* id);
  PathName(const PathName&);                 
public:
 ~PathName() {} 
public:  
  PathName& operator=(const PathName&);  
  PathName& operator=(const Id&);
  PathName& operator=(const char* id);  
public:
  const char* value() const {return _pathname;}
private:
  int _length;    
private:
  char _pathname[128]; 
 };

}

#endif

