
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
 
#ifndef HKS_RELEASEEDITOR
#define HKS_RELEASEEDITOR

#include "hks/Partition.hh"

#include "dsi/Location.hh"
#include "dsi/Set.hh"
#include "dsi/Editor.hh"

namespace HKS {

/*
** Forward references...
*/

class LookupRelease;
class Assign;
class Reset;

class ReleaseEditor : public DSI::Editor {
public:
  ReleaseEditor(const char* partition);
public:
 virtual ~ReleaseEditor() {}
protected:
 void _assign(int argc, char** argv);
 void _reset( int argc, char** argv);
 void _dump(  int argc, char** argv);  
 void _reboot(int argc, char** argv);     
protected:
 void _assign(const DSI::Set& locations, int argc, char** argv);
 void _reset( const DSI::Set& locations, int argc, char** argv);
 void _dump(  const DSI::Set& locations, int argc, char** argv);  
 void _reboot(const DSI::Set& locations, int argc, char** argv);
public:
  void _process(Assign&);
  void _process(Reset&); 
  void _process(LookupRelease&);  
private:
  Partition _partition;
  }; 
                 
}

#endif

