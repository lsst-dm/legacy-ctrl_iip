#include "forwarder/DAQFetcher.h"

PixelArray::PixelArray(const int& d1, const int& d2) : _d1{d1}, _d2{d2} { 
    _arr = new int32_t*[_d1];
    for (int i = 0; i < _d1; i++) { 
        _arr[i] = new int32_t[_d2];
    }
}

PixelArray::~PixelArray() { 
    for (int i = 0; i < _d1; i++) { 
        delete[] _arr[i];
    }
    delete[] _arr; 
}

int32_t** PixelArray::get() { 
    return _arr; 
}
