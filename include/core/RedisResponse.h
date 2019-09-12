#ifndef REDIS_RESPONSE_H
#define REDIS_RESPONSE_H

#include <iostream>
#include "hiredis/hiredis.h"
#include "core/SimpleLogger.h"
#include "core/Exceptions.h"

class RedisResponse { 
    public:
        RedisResponse(redisContext* c, 
                      const char* fmt, 
                      const char* value,
                      size_t size);
        ~RedisResponse();

        bool is_err();
        std::string get_status();
        std::string get_str();
        long long get_int();
        const std::vector<std::string> get_arr();

    private:
        redisReply* _reply;
};

#endif
