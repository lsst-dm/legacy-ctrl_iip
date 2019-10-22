/*
 * This file is part of dm_forwarder
 *
 * Developed for the LSST Data Management System.
 * This product includes software developed by the LSST Project
 * (https://www.lsst.org).
 * See the COPYRIGHT file at the top-level directory of this distribution
 * for details of code ownership.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

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
