#include "core/SimpleLogger.h"
#include "core/Exceptions.h"
#include "core/RedisResponse.h"

RedisResponse::RedisResponse(redisContext* c, 
                             const char* fmt, 
                             const char* value,
                             size_t size) { 
    _reply = static_cast<redisReply*>(redisCommand(c, fmt, value, size)); 
    if (is_err()) {
        std::string err = "Cannot execute command because " + 
            std::string(_reply->str);
        LOG_CRT << err;
        throw L1::RedisError(err);
    }
}

RedisResponse::~RedisResponse() { 
    freeReplyObject(_reply);
}

bool RedisResponse::is_err() { 
    if (_reply->type == REDIS_REPLY_ERROR) { 
        return true;
    }
    return false;
}

std::string RedisResponse::get_status() { 
    if (_reply->type != REDIS_REPLY_STATUS) { 
        LOG_CRT << _reply->str;
        throw L1::RedisError(_reply->str);
    }
    return _reply->str;
}

std::string RedisResponse::get_str() { 
    if (_reply->type == REDIS_REPLY_NIL) { 
        std::string err = "Value for given key is nil";
        LOG_CRT << err;
        throw L1::RedisError(err);
    }
    return _reply->str;
}

long long RedisResponse::get_int() { 
    if (_reply->type != REDIS_REPLY_INTEGER) { 
        LOG_CRT << _reply->str;
        throw L1::RedisError(_reply->str);
    }
    return _reply->integer;
}

const std::vector<std::string> RedisResponse::get_arr() { 
    if (_reply->type != REDIS_REPLY_ARRAY) { 
        LOG_CRT << _reply->str;
        throw L1::RedisError(_reply->str);
    }

    std::size_t num = _reply->elements;
    std::vector<std::string> v(num);
    for (int i = 0; i < num; i++) { 
        v[i] = _reply->element[i]->str; 
    }
    return v;
}
