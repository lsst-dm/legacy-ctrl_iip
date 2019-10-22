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

#include <iostream>
#include <vector>
#include "core/SimpleLogger.h"
#include "core/Exceptions.h"
#include "forwarder/Formatter.h"

#define NUM_AMP 16

namespace fs = boost::filesystem;

std::vector<std::string> excluded_keywords { 
    "BITPIX",
    "NAXIS",
    "PCOUNT",
    "GCOUNT",
    "XTENSION"
};


void FitsFormatter::write_header(const std::vector<std::string>& pattern,
                                 const fs::path& pix_path, 
                                 const fs::path& header_path) { 
    try { 
        int status = 0;
        FitsOpener pix_file(pix_path, READWRITE);
        fitsfile* pix = pix_file.get();

        FitsOpener header_file(header_path, READONLY);
        fitsfile* header = header_file.get();
        
        if (pix_file.num_hdus() != header_file.num_hdus()) { 
            std::string err = "Pixel and header files have different number of HDUs.";
            LOG_CRT << err;
            throw L1::CannotFormatFitsfile(err);
        }

        for (int i = 1; i <= pix_file.num_hdus(); i++) { 
            fits_movabs_hdu(header, i, IMAGE_HDU, &status);
            int segment_num = i;

            // escape primary hdu
            if (i != 1) { 
                segment_num = get_segment_num(pattern, header); 
            }
            fits_movabs_hdu(pix, segment_num, IMAGE_HDU, &status);
          
            int header_keys = 0;
            fits_get_hdrspace(header, &header_keys, NULL, &status); 
            for (int j = 1; j <= header_keys; j++) { 
                char keyname[FLEN_KEYWORD], value[FLEN_VALUE], 
                     comment[FLEN_COMMENT], card[FLEN_CARD];
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
            LOG_CRT << err;
            throw L1::CannotFormatFitsfile(std::string(err));
        }
        LOG_INF << "Finished assembling header with pixel data file.";
    } 
    catch (L1::CfitsioError& e) { 
        throw L1::CannotFormatFitsfile(e.what());
    }
}

bool FitsFormatter::contains_excluded_key(const char* key) { 
    std::string keyword(key);
    auto it = find(excluded_keywords.begin(), excluded_keywords.end(), keyword);
    if (it != excluded_keywords.end()) { 
        return true; 
    }
    return false;
}

int FitsFormatter::get_segment_num(const std::vector<std::string>& pattern, 
                                   fitsfile* header) { 
    int status = 0;
    char segment_value[FLEN_VALUE], segment_comment[FLEN_COMMENT];
    fits_read_key(header, TSTRING, "EXTNAME", segment_value, 
            segment_comment, &status);

    std::string segment = std::string(segment_value);
    std::string segment_idx = segment.substr(segment.length() - 2);
    auto idx_it = std::find(pattern.begin(), pattern.end(), segment_idx);

    if (idx_it == pattern.end()) { 
        std::string err = "Segment " + segment_idx + 
            " is not defined in Readout Pattern."; 
        LOG_CRT << err;
        throw L1::CannotFormatFitsfile(err);
    }
    int idx = std::distance(pattern.begin(), idx_it);

    // +2 because fitsfile indexing is 1 based, instead of 0 based and +1 for 
    // escaping primary hdu
    int segment_num = idx + 2;
    if (status) { 
        char err[FLEN_ERRMSG];
        fits_read_errmsg(err);
        LOG_CRT << err;
        throw L1::CannotFormatFitsfile(std::string(err));
    }
    return segment_num;
}
