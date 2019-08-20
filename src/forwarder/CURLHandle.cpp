#include "core/Exceptions.h"
#include "forwarder/HeaderFetcher.h"

CURLHandle::CURLHandle() { 
    _handle = curl_easy_init();
    if (!_handle) { 
        throw L1::NoCURLHandle("Cannot create curl handle.");
    }
}

CURLHandle::~CURLHandle() { 
    curl_easy_cleanup(_handle);
}

CURL* CURLHandle::get() { 
    return _handle;
}
