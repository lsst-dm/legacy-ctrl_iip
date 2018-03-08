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
 
#ifndef IPV4_SETEXCEPTION
#define IPV4_SETEXECPTION

#include <exception>

namespace IPV4 {

class SetException : public std::exception {
public:  
  SetException() : std::exception() {}
  SetException(int option, bool is_set);
  SetException(int option, int value);
public:   
  SetException(const SetException&);     
public:
  SetException& operator=(const SetException& clone); 
public:
  virtual ~SetException() throw() {}  
public: 
 virtual const char* what() const throw() {return _string;}
private: 
  char _string[128];  
};

}

#endif
