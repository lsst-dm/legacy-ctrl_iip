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
 
#ifndef DSI_EXCEPTION
#define DSI_EXCEPTION

#include <exception>

namespace DSI {

class Exception : public std::exception {
public:  
  Exception(); 
public:  
  Exception(const char* partition);
  Exception(const char* service, const char* partition);
  Exception(const char* service, const char* partition, const char* network);
public:   
  Exception(const Exception&);     
public:
  Exception& operator=(const Exception& clone); 
public:
  virtual ~Exception() throw() {}  
public: 
 virtual const char* what() const throw() {return _string;}
private: 
  char _string[128];  
};

}

#endif
