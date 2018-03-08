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
 
#ifndef DSI_LOCATION
#define DSI_LOCATION

#include <stdint.h>

namespace DSI {

class __attribute__((__packed__)) Location {
public:
  enum {UNDEFINED=128};
  enum {MAX=0x80}; 
public:
  enum {ELEMENT_WIDTH=1, BAY_WIDTH=2, SLOT_WIDTH=4}; // expressed as power of 2...
public:    
  enum {MAX_ELEMENTS = 1 << ELEMENT_WIDTH};
  enum {MAX_BAYS     = 1 << BAY_WIDTH}; 
  enum {MAX_SLOTS    = 1 << SLOT_WIDTH}; 
public:
  enum {ELEMENTS_PER_SLOT = MAX_ELEMENTS * MAX_BAYS};  
public: 
  Location()                 : _location(UNDEFINED) {}
  Location(uint8_t location) : _location(location)  {} 
  Location(unsigned slot, unsigned bay, unsigned element); 
  Location(const char* location);                   
  Location(const char* location, unsigned& span);                   
  Location( const Location& clone) : _location(clone._location) {}
public:  
  Location& operator=(const Location& clone) {_location = clone._location; return *this;}
  Location& operator=(uint8_t clone)         {_location = clone; return *this;}
public:  
  operator bool() const {return _location != UNDEFINED;}
public:  
  Location operator ++(int) {Location location(*this); _location++; return location;}      
public:
 ~Location() {}
public:
  uint8_t index() const {return _location;}      
public:
  const char* presentation(char* buffer) const;
public:  
  void print(int indent=0) const;
private:
  uint8_t _location;
};

}

#endif
