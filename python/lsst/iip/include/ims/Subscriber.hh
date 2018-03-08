
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
 
#ifndef IMS_SUBSCRIBER
#define IMS_SUBSCRIBER

#include "daq/LocationSet.hh"
#include "dss/Subscriber.hh"

#include "linked/List.hh"

#include "ims/Store.hh"

#include "ims/Exception.hh"
#include "ims/Image.hh"
#include "ims/Source.hh"
#include "ims/Slice.hh"

#include "dss/Repository.hh"
#include "dss/RootId.hh"
#include "dss/BranchId.hh"
#include "dss/LeafId.hh"
 
namespace IMS {

class PendingImage;   // Forward reference...
class PendingSource;  // Forward reference...

class Subscriber : public DSS::Subscriber {
public:
  enum {MAX=64}; // Inclusive of NULL termination...
public:
  Subscriber(const Store&, const DAQ::LocationSet&, const char* group) throw (Exception); 
public:  
  virtual ~Subscriber();
public:
  bool wait(char* reason); 
public:
  bool pending();
  bool pending(char* image); 
public:
  bool flush(char* image, DAQ::LocationSet& missing);          
public:
  virtual void process(                             const Image&) = 0;
  virtual void process(const Source&,               const Image&) = 0;
  virtual void process(const Slice&, const Source&, const Image&) = 0;    
private:
  bool process(                                          const DSS::RootId&);
  bool process(const DSS::BranchId&,                     const DSS::RootId&);
  bool process(const DSS::LeafId&, const DSS::BranchId&, const DSS::RootId&);  
private:
  bool M31(const void*, int); // Receive abort request
private:
  PendingImage*  _lookup(  const DSS::RootId&); 
  PendingSource* _allocate(const DSS::BranchId&,               PendingImage*);
  void           _allocate(const DSS::LeafId&, PendingSource*, PendingImage*);
  void           _rundown(PendingImage*);
private:
  Linked::List     _pending; 
  char*            _reason; 
  DSS::RootId      _last; 
  DSS::Repository  _repository;
  DAQ::LocationSet _accepts;
  char             _group[MAX];
  DAQ::Location    _system;
  }; 

}

#endif

