#include <iostream> 
#include "core/Exceptions.h"
#include "core/SimpleLogger.h"
#include "forwarder/HeaderFetcher.h"

using namespace std; 
using namespace boost::filesystem;
using namespace L1;

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
void HeaderFetcher::fetch(const string& url, const path& destination) { 
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
            string err = "Cannot pull header file from " + url + " because " + \
                          string(error_buffer);
            throw NoHeader(err);
        }
        LOG_INF << "Fetched header file from " << url;
    } 
    catch (FileExists& e) { 
        LOG_CRT << e.what() << endl;
    }
    catch (NoCURLHandle& e) { 
        LOG_CRT << e.what() << endl;
    }
}

HeaderFetcher::~HeaderFetcher() { 
    curl_global_cleanup(); 
}
