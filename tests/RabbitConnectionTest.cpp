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

#include <iostream>
#include <boost/test/unit_test.hpp>
#include "core/RabbitConnection.h"
#include "core/IIPBase.h"
#include "core/Exceptions.h"

struct RabbitConnectionFixture : IIPBase {

    std::string _usr, _pwd, _addr;
    std::string _log_dir; 

    RabbitConnectionFixture() : IIPBase("ForwarderCfg.yaml", "test") {
        BOOST_TEST_MESSAGE("Setup RabbitConnection fixture");
        _log_dir = _config_root["LOGGING_DIR"].as<std::string>();

        _usr = _credentials->get_user("service_user");
        _pwd = _credentials->get_passwd("service_passwd"); 
        _addr = _config_root["BASE_BROKER_ADDR"].as<std::string>();
    }

    ~RabbitConnectionFixture() { 
        BOOST_TEST_MESSAGE("TearDown RabbitConnection fixture");
        std::string log = _log_dir + "/test.log.0";
        std::remove(log.c_str());
    }
};

BOOST_FIXTURE_TEST_SUITE(RabbitConnectionSuite, RabbitConnectionFixture);

BOOST_AUTO_TEST_CASE(constructor) {
    // good url
    std::string good_url = "amqp://" + _usr + ":" + _pwd + "@" + _addr;
    BOOST_CHECK_NO_THROW(RabbitConnection r(good_url));

    // bad username, pwd
    std::string bad_url = "amqp://iip:123@" + _addr;
    BOOST_CHECK_THROW(RabbitConnection r(bad_url), L1::RabbitConnectionError);

    // bad ip
    std::string bad_ip = "amqp://" + _usr + ":" + _pwd 
        + "@141.142.238.9:5672/%2fhello";
    BOOST_CHECK_THROW(RabbitConnection r(bad_url), L1::RabbitConnectionError);

    // bad hostname
    std::string hostname = _addr.substr(0, _addr.find("/")) + "/badhost";
    std::string bad_host = "amqp://" + _usr + ":" + _pwd + "@" + hostname;
    BOOST_CHECK_THROW(RabbitConnection r(bad_host), L1::RabbitConnectionError);

    // random string
    BOOST_CHECK_THROW(RabbitConnection r("helloworld"), 
            L1::RabbitConnectionError);
}

BOOST_AUTO_TEST_SUITE_END()
