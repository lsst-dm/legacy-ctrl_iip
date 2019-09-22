#define BOOST_TEST_DYN_LINK 1

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

BOOST_FIXTURE_TEST_SUITE(s, RedisConnectionFixture);

/**
BOOST_AUTO_TEST_CASE(constructor) {
    BOOST_CHECK_NO_THROW(_redis);
    BOOST_CHECK_THROW(RedisConnection r("141.142.238.10", 6379), L1::RedisError);
    BOOST_CHECK_THROW(RedisConnection r("host1", 6379), L1::RedisError);
    BOOST_CHECK_THROW(RedisConnection r("host1", 637), L1::RedisError);
}

BOOST_AUTO_TEST_CASE(select) { 
    BOOST_CHECK_NO_THROW(_redis.select(10)); 
    BOOST_CHECK_THROW(_redis.select(20), L1::RedisError); 
    BOOST_CHECK_THROW(_redis.select(-1), L1::RedisError); 
}

BOOST_AUTO_TEST_CASE(lpush) { 
    std::vector<std::string> v1{"hello", "world"};
    _redis.lpush("key", v1);
    std::vector<std::string> v2 = _redis.lrange("key", 0, -1);
    BOOST_CHECK_EQUAL(v1.size(), v2.size());

    // empty string is valid
    std::vector<std::string> v3{"", ""};
    _redis.lpush("val", v3);
    std::vector<std::string> v4 = _redis.lrange("val", 0, -1);
    BOOST_CHECK_EQUAL(v3.size(), v4.size());

    // cannot push empty vector
    std::vector<std::string> v5;
    BOOST_CHECK_THROW(_redis.lpush("foo", v5), L1::RedisError);
}

BOOST_AUTO_TEST_CASE(del) { 
    _redis.set("foo", "bar");  
    _redis.del("foo");
    BOOST_CHECK_EQUAL(_redis.exists("foo"), false);
    BOOST_CHECK_THROW(_redis.del("foo"), L1::RedisError);
}

BOOST_AUTO_TEST_CASE(flushdb) { 
    _redis.set("foo", "bar");  
    _redis.flushdb();
    BOOST_CHECK_EQUAL(_redis.exists("foo"), false);
}

BOOST_AUTO_TEST_CASE(set) { 
    _redis.set("foo", "bar");
    BOOST_CHECK_EQUAL(_redis.exists("foo"), true);
    BOOST_CHECK_EQUAL(_redis.exists("for"), false);
}

BOOST_AUTO_TEST_CASE(get) { 
    _redis.set("foo", "bar");
    std::string bar = _redis.get("foo");

    BOOST_CHECK_EQUAL("bar", bar);

    // key not exist
    BOOST_CHECK_THROW(_redis.get("for"), L1::RedisError);

    // wrong type of key
    std::vector<std::string> v1{"hello", "world"};
    _redis.lpush("key", v1);
    BOOST_CHECK_THROW(_redis.get("key"), L1::RedisError);
}
*/
BOOST_AUTO_TEST_SUITE_END()
