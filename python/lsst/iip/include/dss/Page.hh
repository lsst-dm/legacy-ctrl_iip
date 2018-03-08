
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
 
#ifndef DSS_PAGE
#define DSS_PAGE

#include "dss/Id.hh"

#include "net/Endian.hh"

namespace DSS {

class __attribute__((__packed__)) Page {
public:
  Page() {}
  Page(const Id& bucket, uint8_t partition=0) : _bucket(bucket),         _number(0),             _partition(partition)        {} 
  Page(const Page& clone)                     : _bucket(clone._bucket),  _number(clone._number), _partition(clone._partition) {}
public:
 ~Page() {};
public: 
  Page& operator=(const Page& clone) {_bucket = clone._bucket; _number = clone._number; _partition = clone._partition; return *this;}  
public:
  const Id& bucket() const {return _bucket;} 
public:
  uint8_t  partition() const {return _partition;} 
  uint8_t  number()    const {return _number;}
public:   
  void set(uint8_t number) {_number = number; return;} 
public:
  const void* content() const {return (const void*)&this[1];} 
private:
  friend class Summary;    
private:
  Id       _bucket;
  uint8_t  _number;
  uint8_t  _partition;
  uint16_t _pad1;
  uint32_t _pad2;
  };

}

#endif

