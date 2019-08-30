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
#include "core/Exceptions.h"
#include "core/SimpleLogger.h"
#include "forwarder/HeaderFetcher.h"

namespace fs = boost::filesystem;

long TIMEOUT = 2L;

/**
 * Initialize HeaderFetcher for pulling header information
 *
 * NOTE: This function must be called immediately after the program starts and
 * while it is still only one thread before using libcurl at all. Currently 
 * corrupted file/wrong file is not handled. MD5 or CRC should be good.
 */
HeaderFetcher::HeaderFetcher() { 
    /// curl_global_init is not thread safe.
    curl_global_init(CURL_GLOBAL_ALL); 
}

/**
 * Fetch header file from HTTP server
 *
 * @param url HTTP url for the header file
 * @param destination target location for written header file
 */
void HeaderFetcher::fetch(const std::string& url, const fs::path& destination) { 
    try { 
        // set error message array to 0
        char error_buffer[CURL_ERROR_SIZE]; 
        error_buffer[0] = 0;

        FileOpener fp(destination);
        FILE* header_file = fp.get();

        CURLHandle curl_handle;
        CURL* handle = curl_handle.get();
        curl_easy_setopt(handle, CURLOPT_URL, url.c_str());
        curl_easy_setopt(handle, CURLOPT_WRITEDATA, header_file);
        curl_easy_setopt(handle, CURLOPT_ERRORBUFFER, error_buffer);
        curl_easy_setopt(handle, CURLOPT_FAILONERROR, 1);
        curl_easy_setopt(handle, CURLOPT_NOPROGRESS, 0);
        curl_easy_setopt(handle, CURLOPT_TIMEOUT, TIMEOUT);
        
        CURLcode status = curl_easy_perform(handle);
        if (status != CURLE_OK) { 
            fp.set_remove();
            std::string err = "Cannot pull header file from " + url + " because " + \
                          std::string(error_buffer);
            LOG_CRT << err;
            throw L1::CannotFetchHeader(err);
        }
        LOG_INF << "Fetched header file from " << url;
    } 
    catch (L1::NoCURLHandle& e) { 
        throw L1::CannotFetchHeader(e.what());
    }
}

HeaderFetcher::~HeaderFetcher() { 
    curl_global_cleanup(); 
}
