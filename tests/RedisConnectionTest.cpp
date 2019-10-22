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

#include <boost/test/unit_test.hpp>
#include <vector>
#include <memory>
#include <thread>
#include <chrono>

#include "core/IIPBase.h"
#include "core/RedisConnection.h"
#include "core/Exceptions.h"

struct RedisConnectionFixture : IIPBase {

    std::string _log_dir; 

    RedisConnectionFixture() : IIPBase("ForwarderCfg.yaml", "test"){ 
        BOOST_TEST_MESSAGE("Setup RedisConnectionTest fixture");
        _log_dir = _config_root["LOGGING_DIR"].as<std::string>();

        _host = _config_root["REDIS_HOST"].as<std::string>();
        _port = _config_root["REDIS_PORT"].as<int>();
        _db = _config_root["REDIS_DB"].as<int>();

        _redis = std::unique_ptr<RedisConnection>(new RedisConnection(
                    _host, _port, _db));
    }

    ~RedisConnectionFixture() { 
        BOOST_TEST_MESSAGE("TearDown RedisConnectionTest fixture");
        std::string log = _log_dir + "/test.log.0";
        std::remove(log.c_str());
    }

    std::string _host;
    int _port, _db;
    std::unique_ptr<RedisConnection> _redis;
};

BOOST_FIXTURE_TEST_SUITE(RedisConnectionSuite, RedisConnectionFixture);

BOOST_AUTO_TEST_CASE(constructor) {
    // good
    BOOST_CHECK_NO_THROW(RedisConnection r(_host, _port, _db));

    // bad host
    BOOST_CHECK_THROW(RedisConnection r("host1", _port, _db), L1::RedisError);

    // bad port
    BOOST_CHECK_THROW(RedisConnection r(_host, 637, _db), L1::RedisError);

    // bad database
    BOOST_CHECK_THROW(RedisConnection r(_host, _port, 25), L1::RedisError);
}

BOOST_AUTO_TEST_CASE(setex) {
    _redis->setex("ping", 3, "pong");

    // true because just set the value
    BOOST_CHECK_EQUAL(_redis->exists("ping"), true); 
    std::this_thread::sleep_for(std::chrono::seconds(5));

    // false because timer expired and value should be gone
    BOOST_CHECK_EQUAL(_redis->exists("ping"), false); 
}

BOOST_AUTO_TEST_CASE(exists) {
    _redis->setex("ping", 3, "pong");
    BOOST_CHECK_EQUAL(_redis->exists("ping"), true);
    BOOST_CHECK_EQUAL(_redis->exists("iip"), false);
}

BOOST_AUTO_TEST_SUITE_END()
