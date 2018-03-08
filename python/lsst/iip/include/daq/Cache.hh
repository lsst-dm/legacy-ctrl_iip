
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
 
#ifndef DAQ_CACHE
#define DAQ_CACHE

namespace DAQ {

class Cache  {
public:
  Cache();   
  Cache(const char* name, void* buffer);
  Cache(const Cache&);    
public:
  Cache& operator=(const Cache&);
  Cache& operator=(const char*);
public:
 ~Cache() {}
public:
  void flush(void* buffer, int length);
public:
  int size() const {return _length;}    
private:
  int         _length;
  const char* _directory;
  const char* _name;
  const char* _extension;    
 };

}

#endif

