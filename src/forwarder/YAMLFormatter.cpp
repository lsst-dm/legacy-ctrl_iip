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

#include <exception>
#include "core/SimpleLogger.h"
#include "core/Exceptions.h"
#include "forwarder/Formatter.h"

namespace fs = boost::filesystem;

const int NUM_AMP = 16;

void YAMLFormatter::write_header(const std::string& raft,
                                 const std::vector<std::string>& ccds,
                                 const std::vector<std::string>& pattern,
                                 const fs::path& pix_path, 
                                 const fs::path& header_path) { 
    try { 
        int status = 0;
        FitsOpener pix_file(pix_path, READWRITE);
        fitsfile* pix = pix_file.get();

        YAML::Node header = YAML::LoadFile(header_path.string());

        // +1 for primary hdu
        int total_hdus = ccds.size() * NUM_AMP + 1;

        if (pix_file.num_hdus() != total_hdus) { 
            std::string err = "Pixel file has invalid number of HDUs. \
                               Expecting " + std::to_string(total_hdus) + " HDUs";
            LOG_CRT << err;
            throw L1::CannotFormatFitsfile(err);
        }

        for (auto& ccd : ccds) { 
            for (int i = 1; i <= pix_file.num_hdus(); i++) { 
                fits_movabs_hdu(pix, i, IMAGE_HDU, &status);

                // primary hdu
                if (i == 1) { 
                    std::cout << "here" << std::endl;
                    YAML::Node primary = header["PRIMARY"];
                    std::cout << "there" << std::endl;
                    write_section(pix, primary);

                    std::string primary_detail = "PRIMARY_R" + raft + "S" + ccd;
                    std::cout << primary_detail << std::endl;
                    YAML::Node primary_raft = header[primary_detail];
                    write_section(pix, primary_raft);
                }

                std::string segment = "R" + raft + "S" + ccd 
                    + "_Segment" + pattern[i-1];
                YAML::Node segment_n = header[segment];
                write_section(pix, segment_n);
            }
        }

        std::cout << status << std::endl;
        /**
        if (status) { 
            char err[FLEN_ERRMSG];
            fits_read_errmsg(err);
            LOG_CRT << err;
            throw L1::CannotFormatFitsfile(std::string(err));
        }
        */
    }
    catch (L1::CannotFormatFitsfile& e) { } 
    catch (std::exception& e) { 
        std::cout << " I M HERE" << std::endl;
        std::cout << e.what() << std::endl;
        /**
        std::string err = std::string(e.what());
        LOG_CRT << err;
        throw L1::CannotFormatFitsfile(err);
        */
    }
}

void YAMLFormatter::write_section(fitsfile* fptr, const YAML::Node& n) { 
    try { 
    int status = 0;
    for (auto it = n.begin(); it != n.end(); it++) { 
        YAML::Node sub = *it;
        std::string key = sub["keyword"].as<std::string>(); 
        std::cout << key << std::endl;
        std::string value = sub["value"].as<std::string>(); 
        std::string comment = sub["comment"].as<std::string>(); 
        if (value == "null") { 
            fits_write_key_null(fptr, key.c_str(), 
                comment.c_str(), &status);
        }
        else { 
            fits_write_key(fptr, TSTRING, key.c_str(), 
                const_cast<char *>(value.c_str()), comment.c_str(), &status);
        }
    } 

    if (status) { 
        char err[FLEN_ERRMSG];
        fits_read_errmsg(err);
        LOG_CRT << err;
        throw L1::CannotFormatFitsfile(std::string(err));
    }
    }
    catch (L1::CannotFormatFitsfile& e) { 
        std::cout << "HELLO" << e.what() << std::endl;
    }
}
