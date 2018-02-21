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
**	000 - January 09, 2007
**
**  Revision History:
**	None.
**
** --
*/
 
#ifndef ARP_TABLE
#define ARP_TABLE

#include <xaui/Xaui.h>

#include "net/ipv4/Address.hh"
#include "net/ipv4/Interface.hh"
#include "net/rce/Plugin.hh"
#include "net/rce/arp/Frame.hh"
#include "net/rce/arp/Element.hh"
#include "net/rce/arp/List.hh"
#include "net/rce/arp/Queue.hh"
#include "net/rce/arp/FreeList.hh"

namespace ARP  {

class Table {
public:
  static Table* init(const IPV4::Interface* interface);
  static void   lookup(Link::Address*, uint32_t ipv4);
public:
  Table(const IPV4::Interface*, unsigned stride=2048); 
public:
 ~Table() {}
public:
  void insert(const Link::Address&, uint32_t ipv4);
  void remove(uint32_t ipv4); 
  void ingest(Frame*); 
public:
  unsigned length()   const {return _stride + 1;} 
  unsigned occupied();   
public:
  List* seek(List*);
  List* seek() {return seek(_table);}
private:
  Element* _lookup(uint32_t key)       {return _list(key)->lookup(key);}
  int      _insert(Element* element)   {return _list(element->key())->insert(element);}  
  Element* _remove(uint32_t key)       {return _list(key)->remove(key);}  
private:
  const Link::Address& _resolve(uint32_t address);
private:
  List* _list(uint32_t key) {return _table + (_stride & key);}       
private:
  unsigned      _stride;
  List*         _table;
  List*         _end;
  FreeList      _freelist;
  Queue         _pending;
  RCE::Plugin   _plugin;
  IPV4::Address _sender;
  Link::Address _blackhole;
  uint16_t      _pad2;
public:  
  Xaui_Protocol _rehandle;
};

}

#endif
