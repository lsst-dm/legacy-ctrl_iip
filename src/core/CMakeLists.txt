cmake_minimum_required (VERSION 3.1)
project (lsst_iip_core)

# c++11 support
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_BUILD_TYPE RelWithDebInfo)

# Build core objects
set(OBJ
    "Consumer.cpp"
    "Credentials.cpp"
    "FileOpener.cpp"
    "IIPBase.cpp"
    "RabbitConnection.cpp"
    "RedisConnection.cpp"
    "RedisResponse.cpp"
    "SimpleLogger.cpp"
    "SimplePublisher.cpp"
)

add_library(lsst_iip_core SHARED ${OBJ})
target_compile_definitions(lsst_iip_core PUBLIC BOOST_LOG_DYN_LINK)
target_include_directories(lsst_iip_core PUBLIC
    "${IIP_INSTALL_DIR}/include"
    "../../include"
)
