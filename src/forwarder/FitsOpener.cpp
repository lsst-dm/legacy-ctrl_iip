#include "core/Exceptions.h"
#include "forwarder/Formatter.h"

#include <iostream>
using namespace std;
using namespace boost::filesystem;
using namespace L1;

FitsOpener::FitsOpener(const path& filepath, int mode) : _status(0) { 
    if (mode == FILE_MODE::WRITE_ONLY && !exists(filepath)) { 
        fits_create_file(&_fptr, filepath.c_str(), &_status); 
    }
    else if (mode == READWRITE || mode == READONLY && exists(filepath)) { 
        fits_open_file(&_fptr, filepath.c_str(), mode, &_status); 
    }
    else if (mode == FILE_MODE::WRITE_ONLY && exists(filepath)){ 
        throw CfitsioError("Trying to create existing fitsfile " + filepath.string());
    }
    else if (mode == READWRITE || mode == READONLY && !exists(filepath)) { 
        throw CfitsioError("File at " + filepath.string() + " does not exist to read.");
    }

    if (_status) { 
        char err[FLEN_ERRMSG];
        fits_read_errmsg(err);
        throw CfitsioError(string(err));
    }
}

FitsOpener::~FitsOpener() { 
    fits_close_file(_fptr, &_status);
}

fitsfile* FitsOpener::get() { 
    return _fptr;
}

int FitsOpener::num_hdus() { 
    int num_hdus = -1;
    fits_get_num_hdus(_fptr, &num_hdus, &_status);
    return num_hdus; 
}
