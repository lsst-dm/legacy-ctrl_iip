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
 
#ifndef DSS_EXCEPTION
#define DSS_EXCEPTION

#include <stdint.h>
#include <exception>

namespace DSS {

class Exception : public std::exception {
public:
  enum : int32_t {NO_ERROR=0, INVALID_REQUEST=1, NOSUCH_PARTITION=2, NOSUCH_BUCKET=3, NO_IDS=4, OPEN_ERROR=5, DUPLICATE_NAME=6};
public:  
  Exception(); 
public:  
  Exception(int error);
public:   
  Exception(const Exception&);     
public:
  Exception& operator=(const Exception& clone); 
public:
  virtual ~Exception() throw() {}  
public: 
 virtual const char* what() const throw() {return _error;}
private: 
  const char* _error;  
};

}

#endif
