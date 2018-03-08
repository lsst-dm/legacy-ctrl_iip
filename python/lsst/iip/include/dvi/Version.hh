
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
**	000 - , 2007
**
**  Revision History:
**	None.
**
** --
*/
 
#ifndef DVI_VERSION
#define DVI_VERSION

#include "osa/TimeStamp.hh"
#include "net/Endian.hh"

namespace DVI {
  
class  __attribute__((__packed__)) Version {
public:
  Version();
  Version(const Version& clone);   
public:
 ~Version() {}
public: 
  Version& operator=(const Version&);
public:
  OSA::TimeStamp buildTime;  
public:
  unsigned    hash()  const {return Net::Endian::local(_hash);}
  bool        dirty() const {return _dirty;}
  const char* tag()   const {return (const char*)_tag;}
private:
  uint8_t  _dirty;
  uint8_t  _reserved[3];
  uint32_t _hash;
  uint8_t  _tag[32];
};

}
#endif
