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

#include <memory>
#include <yaml-cpp/yaml.h>
#include <boost/test/unit_test.hpp>

#include "core/IIPBase.h"
#include "core/Exceptions.h"
#include "forwarder/ReadoutPattern.h"

struct ReadoutPatternFixture : IIPBase { 

    std::unique_ptr<ReadoutPattern> _p;
    std::string _log_dir; 

    ReadoutPatternFixture() : IIPBase("ForwarderCfg.yaml", "test") { 
        BOOST_TEST_MESSAGE("Setup ReadoutPattern fixture");
        _log_dir = _config_root["LOGGING_DIR"].as<std::string>();
        _p = std::unique_ptr<ReadoutPattern>(new ReadoutPattern(_config_root));
    }

    ~ReadoutPatternFixture() { 
        BOOST_TEST_MESSAGE("TearDown ReadoutPattern fixture");
        std::string log = _log_dir + "/test.log.0";
        std::remove(log.c_str());
    }
};

BOOST_FIXTURE_TEST_SUITE(ReadoutPatternTest, ReadoutPatternFixture); 

BOOST_AUTO_TEST_CASE(constructor) { 
    BOOST_CHECK_NO_THROW(_p); 
}

BOOST_AUTO_TEST_CASE(pattern) { 
    BOOST_CHECK_THROW(_p->pattern("ABC"), L1::InvalidReadoutPattern);
    BOOST_CHECK_EQUAL(_p->pattern("WFS").size(), 16);
    BOOST_CHECK_EQUAL(_p->pattern("ITL")[0], "00");
}

BOOST_AUTO_TEST_SUITE_END()
