
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
 
#ifndef DSI_MEMBERSHIP
#define DSI_MEMBERSHIP

#include "dsi/Set.hh"

namespace DSI {

class Membership {
public: 
  Membership(const char* name, const char* path);
public:
 ~Membership() {}
 public: 
  const Set& current() {return _set[0];} 
public: 
  void assign(const Set& members);
  void remove(const Set& members);
public:  
  const Set* pending(bool& assign) const;      
public:
  void commit();  
private:
  void _flush();
private:
  Set _set[3];  
private:
  const char* _path;
  const char* _name;
  };
      
}

#endif

