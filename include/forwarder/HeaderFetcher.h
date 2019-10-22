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

#ifndef HEADERFETCHER_H
#define HEADERFETCHER_H

#include <boost/filesystem.hpp>
#include <curl/curl.h>
#include <stdio.h>

class HeaderFetcher { 
    public:
        HeaderFetcher();
        ~HeaderFetcher();
        void fetch(const std::string&, const boost::filesystem::path&);
  
    private:
        CURL* handle;
};

class FileOpener { 
    public:
        FileOpener(const boost::filesystem::path&);
        ~FileOpener();
        FILE* get();
        void set_remove();

    private:
        FILE* _file;
        bool _remove;
        boost::filesystem::path _filename;
};

class CURLHandle { 
    public:
        CURLHandle();
        ~CURLHandle();
        CURL* get();

    private:
        CURL* _handle;
};

#endif
