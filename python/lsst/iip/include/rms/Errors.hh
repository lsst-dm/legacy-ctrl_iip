
#ifndef RMS_ERRORS
#define RMS_ERRORS

namespace RMS {

enum Errors {SUCCESS         = 0, 
	     INVALID_REQUEST = 1, 
	     EMPTY_REQUEST   = 2, 
	     LINK_DOWN       = 3, 
	     NOT_YET_OPENED  = 4,
	     IN_RESET        = 5,
	     RESET_TIMEOUT   = 6};
}

#endif

