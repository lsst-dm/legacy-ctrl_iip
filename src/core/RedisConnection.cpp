#define BOOST_LOG_DYN_LINK 1

#include <sys/time.h>
#include "core/RedisConnection.h"
#include "core/RedisResponse.h"
#include "core/SimpleLogger.h"
#include "core/Exceptions.h"

RedisConnection::RedisConnection(const std::string& host, const int& port) : _host(host) { 
    // Timeout of 2 seconds for connection handshake
    const struct timeval tv{2, 0};

    _context = redisConnectWithTimeout(host.c_str(), port, tv);
    if (_context->err) { 
        LOG_CRT << _context->errstr;
        throw L1::RedisError(_context->errstr);
    }
}

RedisConnection::~RedisConnection() { 
    redisFree(_context);
}

void RedisConnection::select(int db) { 
    std::ostringstream fmt;
    fmt << "select %b";
    std::string str_db = std::to_string(db);
    RedisResponse response(_context, fmt.str().c_str(), str_db.c_str(), 
            (size_t)str_db.size());
    std::string ok = response.get_status();
}

void RedisConnection::lpush(const char* key, const std::string& value) {
    std::ostringstream fmt;
    fmt << "lpush " << key << " %b";
    RedisResponse r(_context, fmt.str().c_str(), value.c_str(), 
            (size_t)value.size());
}
