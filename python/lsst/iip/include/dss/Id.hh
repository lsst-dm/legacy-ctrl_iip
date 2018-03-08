
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

#ifndef DSS_ID
#define DSS_ID

#include <stdint.h>

namespace DSS {

class __attribute__((__packed__)) Id {
private:
 enum {LEAF=7, BRANCH=6};
public:
  Id();  
  Id(uint64_t id);  
  Id(const char* id);                                
  Id(const Id& clone) {_id.value = clone._id.value;}                               
public:
 ~Id() {} 
public:  
  Id& operator=(const Id& clone) {_id.value = clone._id.value; return *this;}
  Id& operator=(uint64_t clone);
public:
  operator bool() const {return _id.value;}    
public:
  uint64_t value() const;
public:
  bool root()   const {return (_id.element[BRANCH] == 0xFF) && (_id.element[LEAF] == 0xFF);}
  bool branch() const {return (_id.element[BRANCH] != 0xFF) && (_id.element[LEAF] == 0xFF);} 
  bool leaf()   const {return (_id.element[BRANCH] != 0xFF) && (_id.element[LEAF] != 0xFF);}  
protected:
  uint8_t _decodeBranch() const {return _id.element[BRANCH];} 
  uint8_t _decodeLeaf()   const {return _id.element[LEAF];}   
protected:
  void _encodeRoot()                {_id.element[LEAF] = 0xFF; _id.element[BRANCH] = 0xFF;} 
  void _encodeBranch(uint8_t value) {_id.element[LEAF] = 0xFF; _id.element[BRANCH] = value;}
  void _encodeLeaf(uint8_t value)   {_id.element[LEAF] = value;} 
protected:
  void _advanceBranch() {_id.element[BRANCH]++;} 
  void _advanceLeaf()   {_id.element[LEAF]++;}  
private:
   union {uint64_t value; uint8_t element[8];} _id;  
 };

}

#endif

