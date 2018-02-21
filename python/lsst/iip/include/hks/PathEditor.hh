
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
 
#ifndef HKS_PATHEDITOR
#define HKS_PATHEDITOR

#include "dsi/Set.hh"
#include "dsi/Editor.hh"
#include "dsi/Location.hh"

#include "hks/Partition.hh"

namespace HKS {

/*
** Forward references...
*/

class LookupPath;
class Assign;
class Reset;

class PathEditor : public DSI::Editor {
public:
  PathEditor(const char* partition);
public:
 ~PathEditor() {}
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
  void _process(LookupPath&);  
private:
  Partition _partition;
  }; 
                 
}

#endif

