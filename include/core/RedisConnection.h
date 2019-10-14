#ifndef REDIS_CONNECTION_H
#define REDIS_CONNECTION_H

#define BOOST_LOG_DYN_LINK 1
#include <vector>
#include <iostream>
#include <sstream>
#include "hiredis/hiredis.h"
#include "core/RedisResponse.h"
#include "core/SimpleLogger.h"
#include "core/Exceptions.h"

/**
 * Wrapper class for creating a redis connection
 *
 * RedisConnection is a higher level abstraction for hiredis API calls. It
 * implements one method called `command`, which should be used for sending
 * command to redis database.
 *
 * Note: redisContext is not thread-safe.
 */
class RedisConnection {
    public:
        RedisConnection(const std::string& host, 
                        const int& port,
                        const int& db);
        ~RedisConnection();

        void select(int db);
        void lpush(const char* key, const std::string& v);
        void setex(const std::string& key,
                   const int& timeout,
                   const std::string& value);
        bool exists(const std::string& key);

    private:
        std::string _host;
        redisContext* _context;
};

#endif
