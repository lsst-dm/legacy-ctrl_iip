
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
 
#ifndef DSS_BUCKET
#define DSS_BUCKET

#include <stdint.h>

#include "osa/File.hh"
#include "osa/FileException.hh"
#include "dsi/Set.hh"
#include "linked/Element.hh"

namespace DSS {

class Bucket : public Linked::Element {
public:
  enum {PAGE_SIZE2 = 15};
  enum {PAGE_SIZE  = 1 << PAGE_SIZE2};
  enum {BASE=512}; 
public:  
  static void unmap(char* pages, unsigned size) {OSA::File::unmap(pages, size);}
public:
  Bucket(const char* pathname)                   throw(OSA::FileException);  // open
  Bucket(const char* pathname, const char* link) throw(OSA::FileException);  // create
public:
 ~Bucket() {}
public: 
  DSI::Set pending;   
public:
  operator bool() const {return _file;}   
public:
  uint64_t id() const {return _id;} 
public: 
  unsigned size() const {return _file.size();}
public:
  int fetch(void* buffer, unsigned length, unsigned offset=0) {return _file.read(offset, buffer, length);} 
public:   
  int commit(const void* buffer, unsigned length, unsigned page=0);
public:
  char* map(unsigned size) {return _file.map(size);}  
private:
  uint64_t  _id;
  OSA::File _file;
  };

}

#endif

