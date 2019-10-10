cmake_minimum_required (VERSION 3.1)
project (lsst_iip_tests)

# c++11 support
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_BUILD_TYPE RelWithDebInfo)

#set(ENV{IIP_CONFIG_DIR} "./")
# Build forwarder objects
set(OBJ
    "RabbitConnectionTest.cpp"
    "RedisConnectionTest.cpp"
    "ReadoutPatternTest.cpp"
    "miniforwarderTest.cpp"
)

add_library(lsst_iip_tests SHARED ${OBJ})
target_compile_definitions(lsst_iip_tests PRIVATE BOOST_LOG_DYN_LINK)
target_compile_definitions(lsst_iip_tests PRIVATE BOOST_TEST_DYN_LINK)
target_include_directories(lsst_iip_tests PRIVATE
    "${DAQ_DIR}/include"
    "${IIP_INSTALL_DIR}/include"
    "../../include"
)

# Build test executable
add_executable(test_exe Runner.cpp)
target_compile_definitions(test_exe PRIVATE BOOST_LOG_DYN_LINK)
target_compile_definitions(test_exe PRIVATE BOOST_TEST_DYN_LINK)
target_include_directories(test_exe PRIVATE
    "${DAQ_DIR}/include"
    "${IIP_INSTALL_DIR}/include"
    "../../include"
)
target_link_libraries(test_exe PUBLIC
    lsst_iip_forwarder
    lsst_iip_core
    "${daq_ims}"
    "${daq_daq}"
    "${daq_dsi}"
    "${boost_log}"
    "${boost_filesystem}"
    "${boost_system}"
    "${boost_thread}"
    "${boost_unit_test_framework}"
    "cfitsio"
    "${yaml-cpp}"
    "pthread"
    "curl"
    "SimpleAmqpClient"
    "hiredis"
)

set(FWD_TESTS 
    "RabbitConnectionTest/constructor"
    "ReadoutPatternTest/constructor"
    "ReadoutPatternTest/pattern"
    "RedisConnectionTest/constructor"
    "miniforwarderTest/end_readout"
    "miniforwarderTest/check_valid_board"
)

foreach (x ${FWD_TESTS})
    add_test(NAME ${x} COMMAND test_exe --run_test=${x})
endforeach()
set_property(TEST ${FWD_TESTS} PROPERTY ENVIRONMENT IIP_CONFIG_DIR=${IIP_CONFIG_DIR})
