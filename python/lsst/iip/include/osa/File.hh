
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
 
#ifndef OSA_FILE
#define OSA_FILE

#include <stdio.h>
#include <fcntl.h> // Needed for access flags...

#include "osa/FileException.hh"

namespace OSA {

class File {
public:
 enum : mode_t {ACCESS1=((S_IRUSR | S_IWUSR | S_IXUSR) | (S_IRGRP | S_IXGRP) | (S_IROTH | S_IXOTH))};
 enum : mode_t {ACCESS2=((S_IRUSR | S_IWUSR)           | (S_IRGRP | S_IWGRP) | (S_IROTH | S_IWOTH))};
public: 
 static int directory(const char* pathname,                 mode_t access=ACCESS1);
 static int directory(const char* path1, const char* path2, mode_t access=ACCESS1);
public:  
  static void unmap(char* pages, unsigned size); 
public:
  File(const char* pathname,                                      int flags, mode_t access=ACCESS2) throw(FileException);
  File(const char* path, const char* name, const char* extension, int flags, mode_t access=ACCESS2) throw(FileException);
public:
 ~File();
public:
  operator bool() const {return _file;}  
public:
  unsigned size() const; 
public:
  int read(unsigned offset, void* buffer, unsigned length);
  int read(void* buffer);
public:
  int write(unsigned offset, const void* buffer, unsigned length);
  int write(const void* buffer);
public:
  int flush(unsigned offset, void* buffer, unsigned length);
  int flush(void* buffer);
public:
  char* map(unsigned size);   
public:
  void truncate(unsigned size);  
private:
  int   _fd;
  FILE* _file;
};

}

#endif

