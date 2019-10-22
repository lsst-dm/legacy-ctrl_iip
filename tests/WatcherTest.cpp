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

#include <atomic>
#include <functional>
#include <thread>
#include <chrono>
#include <boost/test/unit_test.hpp>
#include "core/HeartBeat.h"
#include "core/RedisConnection.h"
#include "core/IIPBase.h"

std::atomic<bool> flag{true};

void execute() { 
    flag = false;
}

struct WatcherFixture : IIPBase {

    std::unique_ptr<Watcher> _watcher;
    std::unique_ptr<RedisConnection> _redis;

    heartbeat_params _hb;
    std::string _log_dir;
    std::string _key;
    int _timeout;

    WatcherFixture() : IIPBase("ForwarderCfg.yaml", "test") { 
        BOOST_TEST_MESSAGE("Setup Watcher fixture");
        _log_dir = _config_root["LOGGING_DIR"].as<std::string>();

        const std::string host = _config_root["REDIS_HOST"].as<std::string>();
        const int port = _config_root["REDIS_PORT"].as<int>();
        const int db = _config_root["REDIS_DB"].as<int>();

        _timeout = _config_root["CHECK_TIMEOUT"].as<int>();
        _key = "atarchiver_association";

        _hb.redis_host = host;
        _hb.redis_port = port;
        _hb.redis_db = db;
        _hb.key = _key;
        _hb.timeout = _timeout;
        _hb.action = std::bind(execute);

        _watcher = std::unique_ptr<Watcher>(new Watcher());
        _redis = std::unique_ptr<RedisConnection>(new RedisConnection(
                    host, port, db));
    }

    ~WatcherFixture() { 
        BOOST_TEST_MESSAGE("TearDown Watcher fixture");
        std::string log = _log_dir + "/test.log.0";
        std::remove(log.c_str());
    }
};

BOOST_FIXTURE_TEST_SUITE(WatcherSuite, WatcherFixture);

BOOST_AUTO_TEST_CASE(start) {
    // Redis key is set. Then watcher is spawn to check the key. After timeout 
    // passed, watcher checks the value. No one is updating the key. It fails
    // and calls the execute function.
    _redis->setex(_key, _timeout, "value");
    _watcher->start(_hb);
    std::this_thread::sleep_for(std::chrono::seconds(_timeout + 2));
    BOOST_CHECK_EQUAL(flag.load(), false);
    _watcher->clear();

    // Bad Redis hostname is given. Watcher thread cannot start. So, execute is 
    // never called and flag never got set.
    flag = true;
    heartbeat_params hb2 = _hb;
    hb2.redis_host = "141.142.238.00";
    _watcher->start(hb2);
    std::this_thread::sleep_for(std::chrono::seconds(_timeout + 2));
    BOOST_CHECK_EQUAL(flag.load(), true);
    _watcher->clear();
}

BOOST_AUTO_TEST_CASE(clear) {
    // Watcher is started then killed instantly. Execute function wouldn't be
    // called after timeout expired because watcher is dead.
    flag = true;
    _redis->setex(_key, _timeout, "pong");
    Watcher w;
    w.start(_hb);
    // Give watcher some time to spawn
    std::this_thread::sleep_for(std::chrono::seconds(1));
    w.clear();
    std::this_thread::sleep_for(std::chrono::seconds(_timeout));
    BOOST_CHECK_EQUAL(flag.load(), true);
}

BOOST_AUTO_TEST_SUITE_END()
