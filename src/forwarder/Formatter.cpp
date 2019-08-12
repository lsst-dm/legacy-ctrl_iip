#include "core/SimpleLogger.h"
#include "core/Exceptions.h"
#include "forwarder/Formatter.h"

#define NUM_AMP 16

using namespace boost::filesystem;
using namespace L1;

void Formatter::write_pix_file(int32_t** ccd, int32_t& len, long* naxes, const path& filepath) { 
    try { 
        int status = 0;
        int bitpix = LONG_IMG;
        int num_axes = 2;
        int first_elem = 1;

        FitsOpener file(filepath, FILE_MODE::WRITE_ONLY);
        fitsfile* optr = file.get();

        fits_create_img(optr, bitpix, 0, NULL, &status);
        for (int i = 0; i < NUM_AMP; i++) {  
            fits_create_img(optr, bitpix, num_axes, naxes, &status);
            fits_write_img(optr, TINT, first_elem, len, ccd[i], &status);
        }

        if (status) { 
            char err[FLEN_ERRMSG];
            fits_read_errmsg(err);
            throw CfitsioError(string(err));
        }
        LOG_INF << "Finished writing pixel fits file.";
    } 
    catch (CfitsioError& e) { 
        LOG_CRT << e.what();
    }
}
