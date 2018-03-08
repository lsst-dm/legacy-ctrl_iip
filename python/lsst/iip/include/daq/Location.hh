
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
 
#ifndef DAQ_LOCATION
#define DAQ_LOCATION

#include <stdint.h>

namespace DAQ {

class __attribute__((__packed__)) Location  {
public: 
  enum : uint8_t {MAX_BAY=45, SYSTEM=MAX_BAY, MAX_BOARD=2};
public: 
  enum : uint8_t {UNDEFINED=128};
public:  
  Location()                                : _location(UNDEFINED)       {} 
  Location(uint8_t location)                : _location(location)        {} 
  Location(const Location& clone)           : _location(clone._location) {}
  Location(uint8_t bay, uint8_t board);
  Location(const char* Location);
  Location(const char* Location, unsigned& span);
public:
 ~Location() {}
public:
  uint8_t bay()   const;
  uint8_t board() const;
public:  
  uint8_t index() const {return _location;}
public:  
  Location& operator=(const Location& clone) {_location = clone._location; return *this;} 
  Location& operator=(uint8_t location)      {_location = location;        return *this;}
  Location& operator=(const char*); 
public:
  operator bool() const {return _location != UNDEFINED;} 
public:
  const char* presentation(char* buffer) const;         
public:  
  void print(int indent=0) const;
private:
  uint8_t _location;
 };

}

#endif

