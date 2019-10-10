#include <boost/test/unit_test.hpp>
#include <vector>

#include "core/RedisConnection.h"
#include "core/Exceptions.h"

const int db = 10;

struct RedisConnectionFixture {
    /**
     * TODO: Read host name and db from cfg.yaml
     */
    RedisConnectionFixture() : _redis("141.142.238.15", 6379) { 
        BOOST_TEST_MESSAGE("Setup RedisConnectionTest fixture");
        _redis.select(db);
    }

    ~RedisConnectionFixture() { 
        BOOST_TEST_MESSAGE("TearDown RedisConnectionTest fixture");
        // _redis.flushdb();
    }

    RedisConnection _redis;
};

BOOST_FIXTURE_TEST_SUITE(RedisConnectionTest, RedisConnectionFixture);

BOOST_AUTO_TEST_CASE(constructor) {
    BOOST_CHECK_NO_THROW(_redis);
    BOOST_CHECK_THROW(RedisConnection r("141.142.238.10", 6379), L1::RedisError);
    BOOST_CHECK_THROW(RedisConnection r("host1", 6379), L1::RedisError);
    BOOST_CHECK_THROW(RedisConnection r("host1", 637), L1::RedisError);
}

BOOST_AUTO_TEST_SUITE_END()
