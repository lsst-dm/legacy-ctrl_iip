 
#ifndef RMS_INSTRUCTION
#define RMS_INSTRUCTION

#include <inttypes.h>

#include "rms/Fault.hh"

namespace RMS  {

enum {SIZEOF_SPACE = 24};
enum {MAX_ADDRESS = ((1 << SIZEOF_SPACE) - 1)};
  
class __attribute__((__packed__)) Instruction 
{ 
public:
  enum Opcode {GET = 0, PUT = 1, BIS = 2, BIC = 3};
public: 
  Instruction() {}                                        
  Instruction(Opcode, unsigned reg, uint32_t operand=0, Fault fault=OK);
  Instruction(const Instruction& clone) : _operation(clone._operation), _operand(clone._operand) {}
public:
  ~Instruction() {}
public:
  Instruction& operator=(const Instruction&);
public:
  Fault       fault()   const;
  Opcode      opcode()  const;
  unsigned    reg()     const;
  uint32_t    operand() const {return _operand;}
public:
  const char* lookup()              const;
  const char* lookup(Opcode opcode) const;
public:  
  void dump(uint32_t index, int indent=0) const;  
private:
  uint32_t _operation;
  uint32_t _operand;  
};

}

#endif

