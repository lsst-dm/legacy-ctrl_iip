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
 
#ifndef OSA_FILE_EXCEPTION
#define OSA_FILE_EXCEPTION

#include <exception>

namespace OSA {

class FileException : public std::exception {
public:
  enum Access {OPEN=0, READ=1, WRITE=2, FLUSH=3};
public:  
  FileException() : std::exception() {}
  FileException(enum Access, int error, const char* file);  
public:   
  FileException(const FileException&);     
public:
  FileException& operator=(const FileException& clone); 
public:
  virtual ~FileException() throw() {}  
public: 
 virtual const char* what() const throw() {return _string;}
private: 
  char _string[512];  
};

}

#endif
