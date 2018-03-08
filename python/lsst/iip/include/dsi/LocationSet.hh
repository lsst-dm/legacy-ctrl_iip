
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
 
#ifndef DSI_LOCATIONSET
#define DSI_LOCATIONSET

#include "dsi/Set.hh"
#include "dsi/Location.hh"

namespace DSI {

class __attribute__((__packed__)) LocationSet : public Set {
public:
  LocationSet() : Set() {}
public:  
  LocationSet(const Location& location)                   : Set(location.index())       {}
  LocationSet(const LocationSet& a, const LocationSet& b) : Set(a, b)                   {}
  LocationSet(const Location& location, unsigned span)    : Set(location.index(), span) {}
public:
 ~LocationSet() {} 
public:
  bool has(const Location& location) const {return Set::has(location.index());}
  bool had(const Location& location)       {return Set::had(location.index());}
public:
  void insert(const Location& location) {Set::insert(location.index());}
public:
  bool remove(Location& location) {Location convert(Set::remove()); location = convert; return (bool)convert;} 
public: 
 const char* presentation(char* buffer) const; 
 };

}

#endif

