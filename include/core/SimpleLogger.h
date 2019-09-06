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

#ifndef SIMPLE_LOGGER_H
#define SIMPLE_LOGGER_H

#include <string>
#include <iostream>
#include <boost/smart_ptr/shared_ptr.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/log/support/date_time.hpp>
#include <boost/log/common.hpp>
#include <boost/log/expressions.hpp>
#include <boost/log/attributes.hpp>
#include <boost/log/sinks.hpp>
#include <boost/log/sources/severity_logger.hpp>
#include <boost/log/utility/setup/common_attributes.hpp> 

namespace logging = boost::log;
namespace attrs = boost::log::attributes;
namespace src = boost::log::sources;
namespace sinks = boost::log::sinks;
namespace expr = boost::log::expressions;
namespace keywords = boost::log::keywords;

typedef sinks::asynchronous_sink< sinks::text_file_backend > file_sink; 

enum severity_level { 
    debug, 
    info, 
    critical,
    warning
}; 

static src::severity_logger< severity_level > lg;
BOOST_LOG_ATTRIBUTE_KEYWORD(severity, "Severity", severity_level); 

/**
 * Overloaded operator << for log statements
 *
 * @param strm input stream
 * @param level severity level for log statement
 * @return output stream
 */
std::ostream& operator<< (std::ostream& strm, severity_level level);

/**
 * Initializes log file
 *
 * Creates logging sinks, set up filters and log statements output format
 *
 * @param filepath log file directory
 * @param filenaem log file name
 */
void init_log(const std::string& filepath, const std::string& filename);

#define LOGGER(lg_, sev) BOOST_LOG_SEV(lg_, sev) \
    << std::left\
    << "    "\
    << std::setw(30) << std::setfill(' ') << __FILE__\
    << std::setw(30) << std::setfill(' ') << __FUNCTION__\
    << std::setw(5) << std::setfill(' ') << __LINE__\
    << "    "

#define LOG_DBG LOGGER(lg, debug)  
#define LOG_INF LOGGER(lg, info)  
#define LOG_CRT LOGGER(lg, critical)  
#define LOG_WRN LOGGER(lg, warning)  

BOOST_LOG_INLINE_GLOBAL_LOGGER_DEFAULT(lg, src::severity_logger_mt< severity_level >);

#endif
