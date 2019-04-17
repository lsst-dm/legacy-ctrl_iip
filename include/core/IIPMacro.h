#ifndef IIPMACRO_H
#define IIPMACRO_H

#define LOGGER(lg_, sev) BOOST_LOG_SEV(lg_, sev) \
    << std::left\
    << "    "\
    << std::setw(30) << std::setfill(' ') << __FILE__\
    << std::setw(30) << std::setfill(' ') << __FUNCTION__\
    << std::setw(5) << std::setfill(' ') << __LINE__\
    << "    "

#define LOG_INF LOGGER(lg::get(), info)  
#define LOG_DBG LOGGER(lg::get(), debug)  
#define LOG_CRT LOGGER(lg::get(), critical)  

#endif
