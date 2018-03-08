
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
 
#ifndef HKS_MOUNTPOINTEDITOR
#define HKS_MOUNTPOINTEDITOR

#include "dsi/Set.hh"
#include "dsi/Editor.hh"
#include "dsi/Location.hh"

#include "hks/Partition.hh"

namespace HKS {

/*
** Forward references...
*/

class LookupMountpoint;
class Assign;
class Reset;

class MountpointEditor : public DSI::Editor {
public:
  MountpointEditor(const char* partition);
public:
 ~MountpointEditor() {}
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
private:
 void _process(Assign&);
 void _process(Reset&); 
 void _process(LookupMountpoint&);     
private:
  Partition _partition;
  }; 
                 
}

#endif

