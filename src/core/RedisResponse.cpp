/*
 * This file is part of dm_forwarder
 *
 * Developed for the LSST Data Management System.
 * This product includes software developed by the LSST Project
 * (https://www.lsst.org).
 * See the COPYRIGHT file at the top-level directory of this distribution
 * for details of code ownership.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

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

RedisResponse::RedisResponse(redisContext* c, const char* cmd) { 
    _reply = static_cast<redisReply*>(redisCommand(c, cmd)); 
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
