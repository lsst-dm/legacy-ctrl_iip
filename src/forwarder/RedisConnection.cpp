#include <iostream>
#include "hiredis/hiredis.h"
#include "core/RedisResponse.h"
#include "core/SimpleLogger.h"
#include "core/Exceptions.h"

/**
 * Note: redisContext is not thread-safe.
 */
class RedisConnection {
    public:
        RedisConnection(const std::string& ip, const int& port);

        /**
         * Free redis context
         */
        ~RedisConnection();

        /**
         * Sets forwarder
         *
         * @param key Key to set in redis database
         * @param value Value to set in redis database
         */
        void set_fwd(const std::string& key, const std::string& value);

    private:
        std::string _ip;
        redisContext* _context;
};

RedisConnection::RedisConnection(const std::string& ip, const int& port) : _ip(ip) { 
    _context = redisConnect(ip.c_str(), port);
    if (_context->err) { 
        LOG_CRT << _context->errstr;
        throw L1::RedisError(_context->errstr);
    }
}

RedisConnection::~RedisConnection() { 
    std::cout << "con: __des__" << std::endl;
    redisFree(_context);
}

void RedisConnection::set_fwd(const std::string& key, const std::string& value) { 
    std::string command = "LPUSH " + key + " " + value;
    RedisResponse response(_context, command);
}

int main() { 
    try { 
    RedisConnection redis("141.142.238.10", 6379);
    redis.set_fwd("forwarder_list", "f99");
    }
    catch (L1::RedisError& e) { 
        std::cout << e.what() << std::endl;
    }
    return 0;
}
