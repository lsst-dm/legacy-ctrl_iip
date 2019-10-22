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

#include <stdlib.h> // setenv
#include <thread>
#include <chrono>
#include <memory>
#include <vector>
#include <boost/filesystem.hpp>
#include <boost/test/unit_test.hpp>
#include <yaml-cpp/yaml.h>

#include "core/IIPBase.h"
#include "core/Exceptions.h"
#include "forwarder/miniforwarder.h"

namespace fs = boost::filesystem;

struct miniforwarderFixture : IIPBase {

    std::unique_ptr<miniforwarder> _fwd;
    YAML::Node _d;
    std::string _log_dir; 

    miniforwarderFixture() : IIPBase("ForwarderCfg.yaml", "test"){ 
        BOOST_TEST_MESSAGE("Setup miniforwarder fixture");
        _log_dir = _config_root["LOGGING_DIR"].as<std::string>();

        _fwd = std::unique_ptr<miniforwarder>(
                new miniforwarder("ForwarderCfg.yaml", "test"));

        _d = YAML::LoadFile("./data/test_data.yaml");
    }

    YAML::Node build_xfer_params(std::string& image_id, 
                                 std::string& raft, 
                                 std::vector<std::string>& ccds) { 
        YAML::Node sub;
        sub["RAFT_LIST"] = raft;
        sub["RAFT_CCD_LIST"] = ccds;
        sub["AT_FWDR"] = "f99";

        YAML::Node d;
        d["MSG_TYPE"] = "AT_FWDR_XFER_PARAMS";
        d["SESSION_ID"] = _d["SESSION_ID"];
        d["IMAGE_ID"] = image_id;
        d["DEVICE"] = "AT";
        d["JOB_NUM"] = _d["JOB_NUM"];
        d["ACK_ID"] = 0;
        d["REPLY_QUEUE"] = "at_foreman_ack_publish";
        d["TARGET_LOCATION"] = _d["TARGET_LOCATION"];
        d["XFER_PARAMS"] = sub;
        return d;
    }

    YAML::Node build_end_readout(std::string& image_id) { 
        YAML::Node d;
        d["MSG_TYPE"] = "AT_FWDR_END_READOUT";
        d["JOB_NUM"] = _d["JOB_NUM"];
        d["SESSION_ID"] = _d["SESSION_ID"];
        d["IMAGE_ID"] = image_id;
        d["ACK_ID"] = 0;
        d["REPLY_QUEUE"] = "at_foreman_ack_publish";
        d["IMAGE_SEQUENCE_NAME"] = "seq_1";
        d["IMAGES_IN_SEQUENCE"] = 100;
        return d;
    }

    ~miniforwarderFixture() { 
        BOOST_TEST_MESSAGE("TearDown miniforwarder fixture");
        std::string log = _log_dir + "/test.log.0";
        std::remove(log.c_str());
    }
};

BOOST_FIXTURE_TEST_SUITE(miniforwarderTest, miniforwarderFixture);

BOOST_AUTO_TEST_CASE(end_readout) {
    std::string image_id = _d["IMAGE_ID"].as<std::string>();
    std::string raft = _d["RAFT_LIST"].as<std::string>();
    std::vector<std::string> ccds = _d["RAFT_CCD_LIST"].as<std::vector<std::string>>();
    std::string fitspath = _config_root["FITS_PATH"].as<std::string>();

    /**
     * end readout without start integration
     */
    YAML::Node er_without_xfer = build_end_readout(image_id);
    BOOST_CHECK_NO_THROW(_fwd->end_readout(er_without_xfer));

    /**
     * non-existing image_id
     */
    std::string bad_img = "aaa";
    YAML::Node xfer_bad_img = build_xfer_params(bad_img, raft, ccds);
    _fwd->xfer_params(xfer_bad_img);

    YAML::Node er_bad_img = build_end_readout(bad_img);
    BOOST_CHECK_NO_THROW(_fwd->end_readout(er_bad_img));

    /**
     * bad raft
     */
    std::string bad_raft = "1111";
    YAML::Node xfer_bad_raft = build_xfer_params(image_id, bad_raft, ccds);
    _fwd->xfer_params(xfer_bad_raft);

    YAML::Node er_bad_raft = build_end_readout(image_id);
    BOOST_CHECK_NO_THROW(_fwd->end_readout(er_bad_raft));

    /**
     * bad ccd
     * This must be a question for SLAC. In a board, there are 3 ccds and 9
     * should throw an exception of some kind but maybe this is because NCSA's
     * DAQ is a simulator.
     */
    std::vector<std::string> bad_ccds{ "09" };
    YAML::Node xfer_bad_ccds = build_xfer_params(image_id, raft, bad_ccds);
    _fwd->xfer_params(xfer_bad_ccds); 

    YAML::Node er_bad_ccd = build_end_readout(image_id);
    BOOST_CHECK_NO_THROW(_fwd->end_readout(er_bad_ccd));

    /*
     * valid image
     */
    YAML::Node d = build_xfer_params(image_id, raft, ccds);
    _fwd->xfer_params(d);

    YAML::Node n = build_end_readout(image_id);
    _fwd->end_readout(n);

    for (auto& ccd : ccds) { 
        std::string filename = image_id + "--R" + raft + "S" + ccd + ".fits";
        fs::path filepath = fs::path(fitspath) / fs::path(filename);

        // sleep for file creation
        std::this_thread::sleep_for(std::chrono::seconds(2));

        BOOST_CHECK_EQUAL(fs::exists(filepath), true);
        std::remove(filepath.string().c_str());
    }
}

BOOST_AUTO_TEST_CASE(check_valid_board) {
    BOOST_CHECK_EQUAL(_fwd->check_valid_board("00", "00"), true);
    BOOST_CHECK_EQUAL(_fwd->check_valid_board("00", "11"), false);
    BOOST_CHECK_EQUAL(_fwd->check_valid_board("1111", "00"), false);
}

BOOST_AUTO_TEST_SUITE_END()
