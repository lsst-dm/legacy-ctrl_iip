
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
 
#ifndef DSS_TRANSFER
#define DSS_TRANSFER

#include "dss/Id.hh"
#include "dss/Store.hh"
#include "dss/Page.hh"
#include "dss/Summary.hh"

namespace DSS {

class Transfer {
public:
  enum {PAGE_SIZE2 = 15}; // expressed as factor of 2 (32 KBytes)...
  enum {MAX_PAGES = 128};
  enum {ONE_PAGE = (1 << PAGE_SIZE2)};
public:                         
  Transfer(const Id& bucket, const void* content, int sizeof_content, Store&); 
  Transfer(const Id& bucket, const void* content, int sizeof_content, Store&, const Id& link); 
public:                         
  Transfer(const char* bucket, const void* content, int sizeof_content, Store&); 
  Transfer(const char* bucket, const void* content, int sizeof_content, Store&, const Id& link); 
public:
 ~Transfer() {}
public:
  const Id& id() const {return _current.bucket();}
public:
  int32_t error() const {return _error;}  
private:
  void        _transfer(const void* content, int sizeof_content);  
  const char* _send(const char* content, int length=ONE_PAGE);
  void        _close(int sizeof_lastpage);
  void        _retry(int sizeof_lastpage);
private:
  Page        _current;
  Summary     _pending;
  Store&      _store;
  const char* _content;
  int32_t     _error;
  };
 
}

#endif

