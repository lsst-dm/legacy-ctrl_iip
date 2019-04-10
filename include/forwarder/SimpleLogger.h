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

#define LOGGER(lg_, sev) BOOST_LOG_SEV(lg_, sev) \
    << std::left\
    << "    "\
    << std::setw(30) << std::setfill(' ') << __FILE__\
    << std::setw(30) << std::setfill(' ') << __FUNCTION__\
    << std::setw(5) << std::setfill(' ') << __LINE__\
    << "    "\

enum severity_level { 
    debug, 
    info, 
    critical
}; 

BOOST_LOG_ATTRIBUTE_KEYWORD(severity, "Severity", severity_level); 

std::ostream& operator<< (std::ostream& strm, severity_level level) { 
    static const char* log_levels[] = { 
        "debug", 
        "info", 
        "critical"
    }; 

    if (static_cast< std::size_t >(level) < sizeof(log_levels) / sizeof(*log_levels)) { 
        strm << log_levels[level]; 
    } 
    else { 
        strm << static_cast< int >(level); 
    } 
    return strm;
} 

void init_log(std::string filename) { 
    logging::add_common_attributes(); 
    boost::shared_ptr< file_sink > sink(new file_sink(
        keywords::file_name = filename + "_%Y-%m-%d_%N.log", 
        keywords::rotation_size = 1 * 1024 * 1024, 
        keywords::auto_flush = true
    ));  

    sink->set_formatter(
        expr::stream
            << std::left
            << std::setw(10) << std::setfill(' ') << severity
            << expr::format_date_time< boost::posix_time::ptime >("TimeStamp", "%Y-%m-%d %H:%M:%S") 
            << expr::smessage
    ); 

    sink->locked_backend()->set_file_collector(sinks::file::make_collector(
        keywords::target = "logs",
        keywords::max_files = 10
    )); 

    logging::core::get()->add_sink(sink); 
} 
