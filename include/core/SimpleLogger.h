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

BOOST_LOG_ATTRIBUTE_KEYWORD(severity, "Severity", severity_level); 

std::ostream& operator<< (std::ostream&, severity_level);
void init_log(std::string, std::string);

#endif
