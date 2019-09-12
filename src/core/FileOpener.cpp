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

#include "core/Exceptions.h"
#include "core/SimpleLogger.h"
#include "forwarder/HeaderFetcher.h"

namespace fs = boost::filesystem;

FileOpener::FileOpener(const fs::path& file) : _remove(false), _filename(file) { 
    if (fs::exists(file)) { 
        // Removing is safe for synchronous application. If there is
        // asynchronous access to file. remove should be carefully
        // handled.
        std::string wrn = "Going to overwrite existing header file " + file.string();
        LOG_WRN << wrn;
        remove(file.c_str());
    }
    _file = fopen(file.c_str(), "w"); 
}

FileOpener::~FileOpener() { 
    fclose(_file);
    if (_remove) { 
        remove(_filename.c_str());
    }
}

FILE* FileOpener::get() { 
    return _file;
}

void FileOpener::set_remove() {
    _remove = true;
}
