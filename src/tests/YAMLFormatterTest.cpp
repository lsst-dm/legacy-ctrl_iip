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

#define BOOST_TEST_DYN_LINK 1

#include <boost/test/unit_test.hpp>
#include <boost/filesystem.hpp>
#include <vector>
#include "core/Exceptions.h"
#include "forwarder/Formatter.h"

namespace fs = boost::filesystem;

const std::string AT_HEADER = "./data/AT_header.yml";
const std::string AT_PIX = "./data/AT_pixel.fits";
const std::string CFG = "./data/ForwarderCfgTest.yaml";

struct YAMLFormatterFixture {
    YAMLFormatterFixture() {
        BOOST_TEST_MESSAGE("Setup YAMLFormatterTest fixture");
    }

    ~YAMLFormatterFixture() { 
        BOOST_TEST_MESSAGE("TearDown YAMLFormatterTest fixture");
    }

    YAMLFormatter _redis;
};

BOOST_FIXTURE_TEST_SUITE(s, YAMLFormatterFixture);

BOOST_AUTO_TEST_CASE(write_header) {
    std::string test_file = "./data/test.fits";
    copy_file(fs::path(AT_PIX), fs::path(test_file), fs::copy_option::overwrite_if_exists);

    YAMLFormatter _fmt;
    std::vector<std::string> v{ "01" };
    std::vector<std::string> p{ "00", "01", "02", "03", "04", "05", "06", "07",
                                "10", "11", "12", "13", "14", "15", "16", "17" };
    _fmt.write_header("01", v, p, fs::path(test_file), fs::path(AT_HEADER));
}

BOOST_AUTO_TEST_SUITE_END()
