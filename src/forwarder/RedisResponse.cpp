#include "core/RedisResponse.h"

RedisResponse::RedisResponse(redisContext* context, 
                             const std::string& command) { 
    _reply = static_cast<redisReply*>(redisCommand(context, command.c_str()));
    if (_reply->type == REDIS_REPLY_ERROR) { 
        std::cout << "got here" << std::endl;
        std::cout << _reply->str << std::endl;
    }
}

RedisResponse::~RedisResponse() { 
    std::cout << "res: __des__" << std::endl;
    freeReplyObject(_reply);
}
