
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
  
#ifndef RMS_INSTRUCTION_LIST
#define RMS_INSTRUCTION_LIST

#include "rms/Instruction.hh"

namespace RMS  {

class __attribute__((__packed__)) InstructionList 
{
public:
  enum {MAXIMUM = 16};
public:                                         
  InstructionList(uint32_t size=MAXIMUM) :                           _next(0), _size(size) {} 
  InstructionList(const InstructionList&);
  InstructionList(const Instruction& instruction, uint32_t size=1) : _next(1), _size(size) {_instructions[0] = instruction;}
public:
  ~InstructionList() {}
public:
  InstructionList& operator=(const InstructionList&);
public:
  const Instruction* lookup(uint32_t index=0) const {return &_instructions[index];}
public:  
  uint32_t size()  const {return _size;};
  uint32_t level() const {return _next;};
public:  
  void dump(int indent=0) const;
public:
  uint32_t insert(Instruction::Opcode, uint32_t addr, 
		  uint32_t operand=0, Fault fault=OK);
  void     clear() {_next = 0;}
public:
  bool full() const {return _next == _size;}
public:
  operator bool() const {return _next != 0;}
private:
  uint32_t    _next;
  uint32_t    _size;
  Instruction _instructions[MAXIMUM];
  };

}

#endif

