
/*
**  Package:
**	
**
**  Abstract:
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
 
#ifndef IMS_TESTSUBSCRIBER
#define IMS_TESTSUBSCRIBER

#include "daq/LocationSet.hh"
#include "ims/Subscriber.hh"
#include "ims/Store.hh"
#include "ims/Exception.hh"
#include "ims/Image.hh"
#include "ims/Source.hh"
#include "ims/Slice.hh"

namespace IMS {

class TestSubscriber : public Subscriber {
public:
  TestSubscriber(const Store&, const DAQ::LocationSet&, const char* group) throw (Exception); 
public:  
  virtual ~TestSubscriber() {}
public:
  void process(                             const Image&);
  void process(const Source&,               const Image&);
  void process(const Slice&, const Source&, const Image&);    
  }; 

}

#endif

