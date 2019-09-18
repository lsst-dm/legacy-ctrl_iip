#define BOOST_TEST_DYN_LINK 1

#include <memory>
#include <yaml-cpp/yaml.h>
#include <boost/test/unit_test.hpp>
#include "core/Exceptions.h"
#include "forwarder/ReadoutPattern.h"

const std::string TEST_CONFIG = "./config/ForwarderCfgTest.yaml";

struct ReadoutPatternFixture { 

    ReadoutPatternFixture() { 
        YAML::Node node = YAML::LoadFile(TEST_CONFIG); 
        YAML::Node root = node["ROOT"];
        _p = std::unique_ptr<ReadoutPattern>(new ReadoutPattern(root));
    }

    ~ReadoutPatternFixture() { 

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
