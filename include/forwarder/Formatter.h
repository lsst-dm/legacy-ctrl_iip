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

#ifndef FORMATTER_H
#define FORMATTER_H

#include <iostream>
#include <fitsio.h>
#include <boost/filesystem.hpp>
#include <yaml-cpp/yaml.h>

class Formatter { 
    public:
        void write_pix_file(int32_t**, 
                            int32_t&, 
                            long*, 
                            const boost::filesystem::path&);
};

class FitsFormatter : public Formatter { 
    public:
        void write_header(const boost::filesystem::path&, 
                          const boost::filesystem::path&);
        bool contains_excluded_key(const char*);
};

class YAMLFormatter : public Formatter { 
    public:
        void write_header(const std::string& raft,
                          const std::vector<std::string>& ccds,
                          const std::vector<std::string>& pattern,
                          const boost::filesystem::path& pix_path, 
                          const boost::filesystem::path& header_path);
        void write_section(fitsfile* fptr, const YAML::Node& n);
};

class FitsOpener { 
    public:
        FitsOpener(const boost::filesystem::path&, int);
        ~FitsOpener();
        fitsfile* get();
        int num_hdus();
    private:
        fitsfile* _fptr;
        int _status; 
};

enum FILE_MODE { 
    WRITE_ONLY = -1
};

#endif
