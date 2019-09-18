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

#define BOOST_LOG_DYN_LINK 1
#include "core/Exceptions.h"
#include "core/SimpleLogger.h"
#include "forwarder/HeaderFetcher.h"

CURLHandle::CURLHandle() { 
    _handle = curl_easy_init();
    if (!_handle) { 
        std::string err = "Cannot create curl handle";
        LOG_CRT << err;
        throw L1::NoCURLHandle(err);
    }
}

CURLHandle::~CURLHandle() { 
    curl_easy_cleanup(_handle);
}

CURL* CURLHandle::get() { 
    return _handle;
}
