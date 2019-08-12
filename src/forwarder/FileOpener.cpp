#include "core/Exceptions.h"
#include "forwarder/HeaderFetcher.h"

using namespace L1;
using namespace boost::filesystem;

FileOpener::FileOpener(const path& file) : _remove(false), _filename(file) { 
    if (exists(file)) { 
        throw FileExists(file.string() + " exists.");
    }
    _file = fopen(file.c_str(), "w"); 
}

FileOpener::~FileOpener() { 
    fclose(_file);
    if (_remove) { 
        remove(_filename.c_str());
    }
}

FILE* FileOpener::get() { 
    return _file;
}

void FileOpener::set_remove() {
    _remove = true;
}
