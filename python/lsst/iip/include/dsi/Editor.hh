
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
 
#ifndef DSI_EDITOR
#define DSI_EDITOR

#include "dsi/Location.hh"
#include "dsi/LocationSet.hh"

#include "dsi/SymbolTable.hh"

namespace DSI {

class Editor {
public:
  Editor(int argcAssign, int argcRemove, int argcDump, int argcReboot);
public:
 ~Editor() {}
public:
  void announce(); 
public:
  void start();
protected:
 virtual void _assign(int argc, char** argv) {return;}
 virtual void _reset( int argc, char** argv) {return;}
 virtual void _dump(  int argc, char** argv) {return;}  
 virtual void _reboot(int argc, char** argv) {return;}   
protected:
 virtual void _assign(const Set& locations, int argc, char** argv) {return;}
 virtual void _reset( const Set& locations, int argc, char** argv) {return;}
 virtual void _dump(  const Set& locations, int argc, char** argv) {return;}  
 virtual void _reboot(const Set& locations, int argc, char** argv) {return;}
public:
  const char* decode(int error, const Location&,    char* buffer) const;
  const char* decode(int error, const LocationSet&, char* buffer) const;
public:
  void report(int error, const Location&)    const;
  void report(int error, const LocationSet&) const;
private: 
 void _parse(const char* input, Set&);
 void _parse_assign(int argc, char** argv);
 void _parse_reset( int argc, char** argv);
 void _parse_dump(  int argc, char** argv); 
 void _parse_reboot(int argc, char** argv);  
private:
  void _help(int argc, char** argv);
  void _quit(int argc, char** argv) {};
private:  
  void _catch(int argc, char** argv);
  void _arg(  int argc, char** argv) {};
private:
  typedef void (Editor::* Function)(int argc, char** argv);       
private:
  void _call(unsigned index, int argc, char** argv) {Function function = _cmnd[index]; (this->*function)(argc, argv); return;}
private:
  unsigned _register(const char* cmnd, Function function, const char* help); 
private:
  enum {MAX=6+2};   
private:
  int         _argcAssign;
  int         _argcRemove; 
  int         _argcDump; 
  int         _argcReboot; 
  SymbolTable _symbol;
  Function    _cmnd[MAX]; 
  const char* _string[MAX]; 
  }; 
                 
}

#endif

