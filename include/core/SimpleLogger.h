#ifndef SIMPLELOGGER_H
#define SIMPLELOGGER_H

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
    critical
}; 

static src::severity_logger< severity_level > lg;
BOOST_LOG_ATTRIBUTE_KEYWORD(severity, "Severity", severity_level); 

std::ostream& operator<< (std::ostream&, severity_level);
void init_log(std::string, std::string);

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

BOOST_LOG_INLINE_GLOBAL_LOGGER_DEFAULT(lg, src::severity_logger_mt< severity_level >);

#endif
