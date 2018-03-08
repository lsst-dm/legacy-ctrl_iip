#ifndef RDS_SOURCE
#define RDS_SOURCE

#include "daq/Source.hh"
#include "rms/InstructionList.hh"

namespace RDS {
class __attribute__((__packed__)) Source : public DAQ::Source
{
public:
  Source() {}
public:
  Source(const char* shelf, DAQ::Sensor::Type, uint8_t path);
  Source(const Source&);
public:
  ~Source() {}
public:
  Source& operator=(const Source&);
public:
  RMS::InstructionList system;
  RMS::InstructionList user;
};
}

#endif
