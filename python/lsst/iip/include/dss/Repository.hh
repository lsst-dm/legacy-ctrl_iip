
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

#ifndef DSS_REPOSITORY
#define DSS_REPOSITORY
 
namespace DSS {

class __attribute__((__packed__)) Repository {
public:  
  Repository() {_repository[0] = 0;}
  Repository(const char* repository, const char* partition); 
  Repository(const char*);                              
  Repository(const Repository&);                              
public:
 ~Repository() {} 
public:  
  Repository& operator=(const Repository&); 
  Repository& operator=(const char*);  
public:
  const char* value() const {return _repository;}
private:
  char _repository[128]; 
 };

}

#endif

