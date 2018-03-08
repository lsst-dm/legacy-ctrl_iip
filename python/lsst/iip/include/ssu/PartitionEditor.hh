
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
 
#ifndef SSU_PARTITIONEDITOR
#define SSU_PARTITIONEDITOR

#include "dsi/Set.hh"
#include "dsi/Editor.hh"

#include "ssu/Shelf.hh"

namespace SSU {

/*
** Forward references...
*/

class Lookup;
class Assign;
class Reset;

class PartitionEditor : public DSI::Editor {
public:
  PartitionEditor();
public:
 ~PartitionEditor() {}
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
 void _process(Lookup&); 
 void _process(Assign&);
 void _process(Reset&); 
private:
  Shelf _shelf;
  }; 
                 
}

#endif
