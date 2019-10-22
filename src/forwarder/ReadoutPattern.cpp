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

#include <algorithm>
#include <vector>
#include "core/Exceptions.h"
#include "core/SimpleLogger.h"
#include "forwarder/ReadoutPattern.h"

const std::string SENSORS = "SENSORS";

ReadoutPattern::ReadoutPattern(const YAML::Node& n) { 
    _root = n;
}

std::vector<std::string> ReadoutPattern::pattern(const std::string& sensor) { 
    try { 
        std::vector<std::string> boards = _root[sensor].as<std::vector<std::string>>();
        return boards;
    }
    catch (YAML::TypedBadConversion<std::vector<std::string>>& e) { 
        std::string err = "YAML Key \"" + sensor + 
            "\" does not exist in configuration file";
        LOG_CRT << err;
        throw L1::InvalidReadoutPattern(err);
    }
}
