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
 
#ifndef DAQ_RELEASE
#define DAQ_RELEASE

#include "daq/Directory.hh"
#include "dvi/Version.hh"

namespace DAQ {

class  __attribute__((__packed__)) Release : public Directory {
public:
  Release();                      
  Release(const char*);
  Release(const Release&);
public:
  Release& operator=(const Release& clone);
  Release& operator=(const char* clone);
public:
 ~Release() {}
public: 
  DVI::Version version;
};

}

#endif
