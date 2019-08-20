#include <iostream>
#include <vector>
#include "core/SimpleLogger.h"
#include "core/Exceptions.h"
#include "forwarder/Formatter.h"

using namespace std;

#define NUM_AMP 16

using namespace std;
using namespace boost::filesystem;
using namespace L1;

vector<string> excluded_keywords { 
    "BITPIX",
    "NAXIS",
    "PCOUNT",
    "GCOUNT",
    "XTENSION"
};


void FitsFormatter::write_header(const path& pix_path, const path& header_path) { 
    try { 
        int status = 0;
        FitsOpener pix_file(pix_path, READWRITE);
        fitsfile* pix = pix_file.get();

        FitsOpener header_file(header_path, READONLY);
        fitsfile* header = header_file.get();
        
        if (pix_file.num_hdus() != header_file.num_hdus()) { 
            throw CannotFormatFitsfile("Pixel and header files have different number of HDUs.");
        }

        for (int i = 1; i <= pix_file.num_hdus(); i++) { 
            fits_movabs_hdu(pix, i, IMAGE_HDU, &status);
            fits_movabs_hdu(header, i, IMAGE_HDU, &status);
            
            int header_keys = 0;
            fits_get_hdrspace(header, &header_keys, NULL, &status); 

            for (int j = 1; j <= header_keys; j++) { 
                char keyname[FLEN_KEYWORD], value[FLEN_VALUE], comment[FLEN_COMMENT], card[FLEN_CARD];
                fits_read_keyn(header, j, keyname, value, comment, &status); 

                if (!contains_excluded_key(keyname)) { 
                    fits_read_record(header, j, card, &status);
                    fits_write_record(pix, card, &status);
                }
            }
        }

        if (status) { 
            char err[FLEN_ERRMSG];
            fits_read_errmsg(err);
            throw CfitsioError(string(err));
        }
        LOG_INF << "Finished assembling header with pixel data file.";
    } 
    catch (CfitsioError& e) { 
        LOG_CRT << e.what();
    }
}

bool FitsFormatter::contains_excluded_key(char* key) { 
    string keyword(key);
    auto it = find(excluded_keywords.begin(), excluded_keywords.end(), keyword);
    if (it != excluded_keywords.end()) { 
        return true; 
    }
    return false;
}
