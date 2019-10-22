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

#include "core/SimpleLogger.h"

std::ostream& operator<< (std::ostream& strm, severity_level level) { 
    static const char* log_levels[] = { 
        "debug", 
        "info", 
        "critical",
        "warning"
    }; 

    if (static_cast< std::size_t >(level) < sizeof(log_levels) / sizeof(*log_levels)) { 
        strm << log_levels[level]; 
    } 
    else { 
        strm << static_cast< int >(level); 
    } 
    return strm;
} 

void init_log(const std::string& filepath, const std::string& filename) { 
    logging::add_common_attributes(); 
    logging::core::get()->add_global_attribute("UTCTime", attrs::utc_clock());
    boost::shared_ptr< file_sink > sink(new file_sink(
        keywords::file_name = filepath + "/" + filename + ".log.%N", 
        keywords::rotation_size = 1 * 1024 * 1024, 
        keywords::auto_flush = true,
        keywords::open_mode = std::ios_base::app
    ));  

    sink->set_formatter(
        expr::stream
            << std::left
            << std::setw(10) << std::setfill(' ') << severity
            << expr::format_date_time< boost::posix_time::ptime >("UTCTime", "%Y-%m-%d %H:%M:%S.%f") 
            << expr::smessage
    ); 

    sink->locked_backend()->set_file_collector(sinks::file::make_collector(
        keywords::target = filepath,
        keywords::max_files = 10
    )); 

    logging::core::get()->add_sink(sink); 
} 
