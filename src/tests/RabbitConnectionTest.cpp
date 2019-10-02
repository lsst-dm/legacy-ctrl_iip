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

struct Fixture : IIPBase {
    Fixture() : IIPBase("ForwarderCfgTest.yaml", "RabbitConnectionTest") {
        BOOST_TEST_MESSAGE("Setup fixture");
        _usr = _credentials->get_user("service_user");
        _pwd = _credentials->get_passwd("service_passwd"); 
        _addr = _config_root["BASE_BROKER_ADDR"].as<std::string>();
    }

    ~Fixture() { 
        BOOST_TEST_MESSAGE("TearDown fixture");
        std::remove("./RabbitConnectionTest.log.0");
    }

    std::string _usr, _pwd, _addr;
};

BOOST_FIXTURE_TEST_SUITE(RabbitConnectionTest, Fixture);

BOOST_AUTO_TEST_CASE(constructor) {
    // good url
    std::string good_url = "amqp://" + _usr + ":" + _pwd + "@" + _addr;
    BOOST_CHECK_NO_THROW(RabbitConnection r(good_url));

    // bad username, pwd
    std::string bad_url = "amqp://iip:123@" + _addr;
    BOOST_CHECK_THROW(RabbitConnection r(bad_url), L1::RabbitConnectionError);

    // bad ip
    std::string bad_ip = "amqp://" + _usr + ":" + _pwd + "@141.142.238.9:5672/%2fhello";
    BOOST_CHECK_THROW(RabbitConnection r(bad_url), L1::RabbitConnectionError);

    // bad hostname
    std::string hostname = _addr.substr(0, _addr.find("/")) + "/badhost";
    std::string bad_host = "amqp://" + _usr + ":" + _pwd + "@" + hostname;
    BOOST_CHECK_THROW(RabbitConnection r(bad_host), L1::RabbitConnectionError);

    // random string
    BOOST_CHECK_THROW(RabbitConnection r("helloworld"), L1::RabbitConnectionError);
}

BOOST_AUTO_TEST_SUITE_END()
