#include <thread>
#include <chrono>
#include <memory>
#include <vector>
#include <boost/filesystem.hpp>
#include <boost/test/unit_test.hpp>
#include <yaml-cpp/yaml.h>

#include "core/Exceptions.h"
#include "forwarder/miniforwarder.h"

namespace fs = boost::filesystem;

struct miniforwarderFixture {
    std::unique_ptr<miniforwarder> _fwd;
    YAML::Node _d;
    YAML::Node _root;

    miniforwarderFixture() { 
        BOOST_TEST_MESSAGE("Setup miniforwarder fixture");
        _fwd = std::unique_ptr<miniforwarder>(new miniforwarder());

        YAML::Node cfg = YAML::LoadFile("./config/ForwarderCfgTest.yaml");
        _root = cfg["ROOT"];
        _d = YAML::LoadFile("./data/test_data.yaml");
    }

    YAML::Node build_xfer_params() { 
        std::vector<std::string> v{"00"};
        YAML::Node sub;
        sub["RAFT_LIST"] = _d["RAFT_LIST"];
        sub["RAFT_CCD_LIST"] = _d["RAFT_CCD_LIST"];
        sub["AT_FWDR"] = "f99";

        YAML::Node d;
        d["MSG_TYPE"] = "AT_FWDR_XFER_PARAMS";
        d["SESSION_ID"] = _d["SESSION_ID"];
        d["IMAGE_ID"] = _d["IMAGE_ID"];
        d["DEVICE"] = "AT";
        d["JOB_NUM"] = _d["JOB_NUM"];
        d["ACK_ID"] = 0;
        d["REPLY_QUEUE"] = "at_foreman_ack_publish";
        d["TARGET_LOCATION"] = _d["TARGET_LOCATION"];
        d["XFER_PARAMS"] = sub;
        return d;
    }

    YAML::Node build_end_readout() { 
        YAML::Node d;
        d["MSG_TYPE"] = "AT_FWDR_END_READOUT";
        d["JOB_NUM"] = _d["JOB_NUM"];
        d["SESSION_ID"] = _d["SESSION_ID"];
        d["IMAGE_ID"] = _d["IMAGE_ID"];
        d["ACK_ID"] = 0;
        d["REPLY_QUEUE"] = "at_foreman_ack_publish";
        d["IMAGE_SEQUENCE_NAME"] = "seq_1";
        d["IMAGES_IN_SEQUENCE"] = 100;
        return d;
    }

    ~miniforwarderFixture() { 
        BOOST_TEST_MESSAGE("TearDown miniforwarder fixture");
    }
};

BOOST_FIXTURE_TEST_SUITE(miniforwarderTest, miniforwarderFixture);

BOOST_AUTO_TEST_CASE(end_readout) {
    YAML::Node d = build_xfer_params();
    _fwd->xfer_params(d);

    YAML::Node n = build_end_readout();
    _fwd->end_readout(n);

    std::string fitspath = _root["FITS_PATH"].as<std::string>();
    std::string image_id = _d["IMAGE_ID"].as<std::string>();
    std::string raft = _d["RAFT_LIST"].as<std::string>();
    std::vector<std::string> ccds = _d["RAFT_CCD_LIST"].as<std::vector<std::string>>();
    for (auto& ccd : ccds) { 
        std::string filename = image_id + "--R" + raft + "S" + ccd + ".fits";
        fs::path filepath = fs::path(fitspath) / fs::path(filename);

        // sleep for file creation
        std::this_thread::sleep_for(std::chrono::seconds(2));

        BOOST_CHECK_EQUAL(fs::exists(filepath), true);
        std::remove(filepath.string().c_str());
    }
}

BOOST_AUTO_TEST_SUITE_END()
