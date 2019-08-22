#include <vector>
#include <algorithm>
#include "forwarder/DAQFetcher.h"

PixelArray::PixelArray(const std::vector<std::vector<int32_t>>& vec) { 
    _d1 = vec.size();
    _d2 = vec[0].size(); 

    _arr = new int32_t*[_d1];
    for (int i = 0; i < _d1; i++) { 
        _arr[i] = new int32_t[_d2];
        std::copy(vec[i].begin(), vec[i].end(), _arr[i]);
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
