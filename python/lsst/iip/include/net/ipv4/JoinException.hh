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
 
#ifndef IPV4_JOINEXCEPTION
#define IPV4_JOINEXECPTION

#include <stdint.h>
#include <exception>

namespace IPV4 {

class JoinException : public std::exception {
public:  
  JoinException() : std::exception() {}
  JoinException(uint32_t mcst_group);
public:   
  JoinException(const JoinException&);     
public:
  JoinException& operator=(const JoinException& clone); 
public:
  virtual ~JoinException() throw() {}  
public: 
 virtual const char* what() const throw() {return _string;}
private: 
  char _string[128];  
};

}

#endif
