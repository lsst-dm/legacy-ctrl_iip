/*
 * This file is part of ctrl_iip
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
