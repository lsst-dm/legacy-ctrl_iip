
/*
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
**	    000 - April 06, 2011
**
**  Revision History:
**	    None.
**
** --
*/
 
#ifndef IMS_MESSAGE
#define IMS_MESSAGE

namespace IMS {

class __attribute__((__packed__)) Message {
public:
 enum {MAX=128};
public: 
  Message(const char* content, const char* group);
  Message(const Message&);
public:
 ~Message() {} 
public:
  bool accept(const char* group) const;
public:
  char content[MAX];
private:
  char _group[64];
  };

}

#endif

