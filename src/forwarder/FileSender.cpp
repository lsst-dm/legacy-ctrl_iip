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
#include <sstream>
#include "core/SimpleLogger.h"
#include "core/Exceptions.h"
#include "forwarder/FileSender.h"

namespace fs = boost::filesystem;

void FileSender::send(const fs::path& from, const fs::path& to) { 
    const char* home = getenv("HOME"); 
    fs::path private_key = fs::path(home) / fs::path(".ssh/id_rsa");
    if (!exists(private_key)) { 
        throw L1::CannotCopyFile("Private key does not exist.");
    }

    // -f, forces the copy, if file exists, delete and copy
    // -n, does not use DNS to resolve IP addresses
    std::ostringstream bbcp;
    bbcp << "bbcp"
         << " -f "
         << " -n "
         << " -s 1 "
         << " -i " << private_key << " "
         << from.string()
         << " "
         << to.string();

    int status = system(bbcp.str().c_str());
    if (status) { 
        throw L1::CannotCopyFile("Cannot copy file from " + from.string() + " to " + to.string());
    }

    LOG_INF << "Sent file from " + from.string() + " to " + to.string();
}
