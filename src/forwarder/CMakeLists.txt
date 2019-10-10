cmake_minimum_required (VERSION 3.1)
project (lsst_iip_forwarder)

# c++11 support
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_BUILD_TYPE RelWithDebInfo)

# Build forwarder objects
set(OBJ
    "CURLHandle.cpp"
    "DAQFetcher.cpp"
    "FileSender.cpp"
    "FitsOpener.cpp"
    "FitsFormatter.cpp"
    "Formatter.cpp"
    "HeaderFetcher.cpp"
    "MessageBuilder.cpp"
    "miniforwarder.cpp"
    "PixelArray.cpp"
    "ReadoutPattern.cpp"
    "Scoreboard.cpp"
    "StripeArray.cpp"
)

add_library(lsst_iip_forwarder SHARED ${OBJ})
target_compile_definitions(lsst_iip_forwarder PUBLIC BOOST_LOG_DYN_LINK)
target_include_directories(lsst_iip_forwarder PUBLIC
    "${DAQ_DIR}/include"
    "${IIP_INSTALL_DIR}/include"
    "../../include"
)

# Build forwarder executable
add_executable(iip_forwarder main.cpp)
target_compile_definitions(iip_forwarder PUBLIC BOOST_LOG_DYN_LINK)
target_include_directories(iip_forwarder PUBLIC
    "${YAML_INCLUDE_DIR}"
    "${DAQ_DIR}/include"
    "${IIP_INSTALL_DIR}/include"
    "../../include"
)
target_link_libraries(iip_forwarder PUBLIC
    lsst_iip_forwarder
    lsst_iip_core
    "${daq_ims}"
    "${daq_daq}"
    "${daq_dsi}"
    "${boost_log}"
    "${boost_filesystem}"
    "${boost_system}"
    "${boost_thread}"
    "cfitsio"
    "${yaml-cpp}"
    "pthread"
    "curl"
    "SimpleAmqpClient"
    "hiredis"
)
