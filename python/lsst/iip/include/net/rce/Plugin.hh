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
 
#ifndef RCE_PLUGIN
#define RCE_PLUGIN

#include <stdint.h>    // appears to be necessary for SAS include to compile...

#include "sas/Sas.h"

namespace RCE {

class Plugin {
public: 
  Plugin(unsigned sizeof_header);
public:
 ~Plugin();
public:
  void  post(const uint64_t* header); 
  void  post(const uint64_t* header,                                                                                                     void* payload, unsigned sizeof_payload, bool more);
  void  post(const uint64_t* header, const uint64_t* header1, unsigned sizeof_header1,                                                   void* payload, unsigned sizeof_payload, bool more); 
  void  post(const uint64_t* header, const uint64_t* header1, unsigned sizeof_header1, const uint64_t* header2, unsigned sizeof_header2, void* payload, unsigned sizeof_payload, bool more); 
public:
  void print(int indent=0) const;
private:
  unsigned    _sizeof_header;
  SAS_Session _session;
  SAS_ObMbx   _mbx; 
  SAS_Mbx     _wait; 
  uint32_t    _mid;
};

}

#endif
