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

#include <thread>
#include <boost/test/unit_test.hpp>
#include "core/IIPBase.h"
#include "core/HeartBeat.h"
#include "core/RedisConnection.h"

void test_execute() { 
    // dummy function
}

struct BeaconFixture : IIPBase {

    std::unique_ptr<RedisConnection> _redis;

    heartbeat_params _hb;
    std::string _log_dir;
    std::string _key;
    int _timeout;

    BeaconFixture() : IIPBase("ForwarderCfg.yaml", "test") { 
        BOOST_TEST_MESSAGE("Setup Beacon fixture");
        _log_dir = _config_root["LOGGING_DIR"].as<std::string>();

        const std::string host = _config_root["REDIS_HOST"].as<std::string>();
        const int port = _config_root["REDIS_PORT"].as<int>();
        const int db = _config_root["REDIS_DB"].as<int>();

        _timeout = _config_root["SET_TIMEOUT"].as<int>();
        _key = "f99_association";

        _hb.redis_host = host;
        _hb.redis_port = port;
        _hb.redis_db = db;
        _hb.key = _key;
        _hb.timeout = _timeout;
        _hb.action = std::bind(test_execute);

        _redis = std::unique_ptr<RedisConnection>(new RedisConnection(
                    host, port, db));
    }

    ~BeaconFixture() { 
        BOOST_TEST_MESSAGE("TearDown Beacon fixture");
        std::string log = _log_dir + "/test.log.0";
        std::remove(log.c_str());
    }
};

BOOST_FIXTURE_TEST_SUITE(BeaconSuite, BeaconFixture);

BOOST_AUTO_TEST_CASE(constructor) {
    // A valid Beacon. It should set the key at regular interval and key must 
    // be valid. Thread is slept for 1 second to give Beacon thread time to
    // spawn, otherwise this will fail.
    Beacon b(_hb);
    std::this_thread::sleep_for(std::chrono::seconds(1));
    BOOST_CHECK_EQUAL(_redis->exists(_key), true);
    b.clear();

    // Beacon is given invalid redis host. That should kill the thread. So no
    // one is updating key and the key should expire after timeout.
    heartbeat_params hb = _hb;
    hb.redis_host = "141.142.238.00";
    Beacon b2(hb);
    std::this_thread::sleep_for(std::chrono::seconds(_timeout));
    BOOST_CHECK_EQUAL(_redis->exists(_key), false);
    b2.clear();
}

BOOST_AUTO_TEST_CASE(clear) {
    // Beacon thread is killed, so no one is updating key and key shouldn't 
    // exist after timeout.
    Beacon b(_hb);
    b.clear();
    std::this_thread::sleep_for(std::chrono::seconds(_timeout));
    BOOST_CHECK_EQUAL(_redis->exists(_key), false);
}

BOOST_AUTO_TEST_SUITE_END()
