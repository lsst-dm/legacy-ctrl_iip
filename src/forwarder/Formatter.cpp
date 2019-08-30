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

#include "core/SimpleLogger.h"
#include "core/Exceptions.h"
#include "forwarder/Formatter.h"

#define NUM_AMP 16

namespace fs = boost::filesystem;

void Formatter::write_pix_file(int32_t** ccd, int32_t& len, long* naxes, const fs::path& filepath) { 
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
            LOG_CRT << std::string(err);
            throw L1::CannotFormatFitsfile(err);
        }
        LOG_INF << "Finished writing pixel fits file.";
    } 
    catch (L1::CfitsioError& e) { 
        throw L1::CannotFormatFitsfile(e.what());
    }
}
