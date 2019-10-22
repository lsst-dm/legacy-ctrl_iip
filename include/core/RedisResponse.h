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
        RedisResponse(redisContext* c, const char* cmd); 
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
