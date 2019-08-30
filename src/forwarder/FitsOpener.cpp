/*
 * This file is part of ctrl_iip
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

#include <iostream>
#include <cstdio>
#include "core/Exceptions.h"
#include "core/SimpleLogger.h"
#include "forwarder/Formatter.h"

namespace fs = boost::filesystem;

FitsOpener::FitsOpener(const fs::path& filepath, int mode) : _status(0) { 
    if (mode == FILE_MODE::WRITE_ONLY && !exists(filepath)) { 
        fits_create_file(&_fptr, filepath.c_str(), &_status); 
    }
    else if (mode == READWRITE || mode == READONLY && exists(filepath)) { 
        fits_open_file(&_fptr, filepath.c_str(), mode, &_status); 
    }
    else if (mode == FILE_MODE::WRITE_ONLY && exists(filepath)){ 
        // Removing is safe for synchronous application. If there is
        // asynchronous access to file. remove should be carefully
        // handled.
        std::string wrn = "Going to overwrite existing fitsfile " + filepath.string();
        LOG_WRN << wrn;
        remove(filepath.c_str());
        fits_create_file(&_fptr, filepath.c_str(), &_status); 
    }
    else if (mode == READWRITE || mode == READONLY && !exists(filepath)) { 
        std::string err = "File at " + filepath.string() + " does not exist to read.";
        LOG_CRT << err;
        throw L1::CfitsioError(err);
    }

    if (_status) { 
        char err[FLEN_ERRMSG];
        fits_read_errmsg(err);
        LOG_CRT << err;
        throw L1::CfitsioError(std::string(err));
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
