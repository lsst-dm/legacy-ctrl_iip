#ifndef REDIS_RESPONSE_H
#define REDIS_RESPONSE_H

#include <iostream>
#include "hiredis/hiredis.h"

class RedisResponse { 
    public:
        RedisResponse(redisContext* context, 
                      const std::string& command); 
        ~RedisResponse();

    private:
        redisReply* _reply;
};

#endif
