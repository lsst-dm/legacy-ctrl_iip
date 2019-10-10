#include <memory>
#include <yaml-cpp/yaml.h>
#include <boost/test/unit_test.hpp>

#include "core/Exceptions.h"
#include "core/IIPBase.h"
#include "forwarder/ReadoutPattern.h"

struct ReadoutPatternFixture : IIPBase { 

    ReadoutPatternFixture() : IIPBase("ForwarderCfg.yaml", "test") { 
        BOOST_TEST_MESSAGE("Setup ReadoutPattern fixture");
        _p = std::unique_ptr<ReadoutPattern>(new ReadoutPattern(_config_root));
    }

    ~ReadoutPatternFixture() { 
        BOOST_TEST_MESSAGE("TearDown ReadoutPattern fixture");
        std::string logfile = get_log_filepath() + "/test.log.0";
        std::remove(logfile.c_str());
    }

    std::unique_ptr<ReadoutPattern> _p;
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
