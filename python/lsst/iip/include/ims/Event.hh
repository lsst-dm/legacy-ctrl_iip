
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
 
#ifndef IMS_EVENT
#define IMS_EVENT

#include <stdint.h>

namespace IMS {

class __attribute__((__packed__)) Event  {
public:
  enum Command : uint8_t {ZERO=0, ONE=1, TWO=2, THREE=3, FOUR=4, FIVE=5, SIX=6, SEVEN=7};
public:
  Event()                                   : _command(0),              _partition(0),                _pad1(0),           _pad2(0)           {} 
  Event(Command command, uint8_t partition) : _command(command),        _partition(partition),        _pad1(0),           _pad2(0)           {} 
  Event(const Event& clone)                 : _command(clone._command), _partition(clone._partition), _pad1(clone._pad1), _pad2(clone._pad2) {} 
public:
 ~Event() {}
public: 
  Event& operator=(const Event& clone) {_command = clone._command; _partition = clone._partition; _pad1 = clone._pad1; _pad2 = clone._pad2; return *this;}  
public:
  Command command()   const {return (Command)_command;} 
  uint8_t partition() const {return _partition;} 
private:
  uint8_t  _command;
  uint8_t  _partition;
  uint16_t _pad1;
  uint32_t _pad2;    
  };
  
}

#endif

