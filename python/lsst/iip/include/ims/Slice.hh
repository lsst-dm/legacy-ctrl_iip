
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
 
#ifndef IMS_SLICE
#define IMS_SLICE

#include "ims/Exception.hh"
#include "ims/Store.hh"
#include "ims/Source.hh"

#include "dss/LeafId.hh"
#include "dss/StoredBucket.hh"
#include "dss/Repository.hh"

namespace IMS {
 
class Stripe; // forward reference...
  
class Slice {
public:
  Slice(const Source&)                                              throw(Exception);    
  Slice(const DSS::LeafId&, int numof_ccds, const DSS::Repository&) throw(Exception);  
public:
 ~Slice() {}
public:
  operator bool() const {return _bucket.id();}   
public:
  int stripes() const;
public:
  bool eol() const {return _bucket.eol();}  
public:
  bool advance() {return _bucket.advance();}
private:
  friend class Source;  
private:
  void _remove();          
protected:
  int         _size() const {return _bucket.size();}
  const char* _data() const {return _bucket.content();}
  const char* _decode(const char* input, Stripe* output); 
private:
  int               _numof_ccds;
  DSS::StoredBucket _bucket;   
};

}

#endif

