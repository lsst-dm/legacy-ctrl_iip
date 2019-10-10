cmake_minimum_required (VERSION 3.1)
project (dm_forwarder 
    VERSION 2.1
    DESCRIPTION "Forwarder for LSST DM Project"
    LANGUAGES CXX
)
enable_testing()

# =============================================================================
# strip rpath

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR})
set(CMAKE_SKIP_RPATH TRUE)

# set library versions
set(BOOST_VERSION 1.66.0)
set(YAML-CPP_VERSION 0.5.3)
set(CFITSIO_VERSION 0.5.3)
set(RABBITMQ-C_VERSION 0.5.3)
set(SIMPLE_AMQP_CLIENT_VERSION 0.5.3)
set(HIREDIS_VERSION 0.5.3)

# iip installation path
set(IIP_INSTALL_DIR "/opt/lsst" CACHE STRING "Install directories for libraries and header files for ctrl_iip")
set(IIP_CONFIG_DIR "${PROJECT_SOURCE_DIR}/etc/config" CACHE STRING "IIP_CONFIG_DIR for running ctests")
set(IIP_PACKAGE_REPO "http://lsst-web.ncsa.illinois.edu/~hwin16/packages")

# if DAQ environment variable is set, use that value. Otherwise, set hard-coded
# value
if (DEFINED ENV{EXPORT_ROOT}) 
    set(DAQ_DIR $ENV{EXPORT_ROOT} CACHE STRING "DAQ Libraries root folder")
else()
    set(DAQ_DIR "/srv/nfs/lsst-daq/daq-sdk/current" CACHE STRING "DAQ Libraries root folder")
endif()

# =============================================================================
# find daq libraries path

find_package(Boost ${BOOST_VERSION} EXACT REQUIRED)
#find_package(yaml-cpp ${YAML-CPP_VERSION} EXACT REQUIRED)
#find_package(cfitsio 0.5.3)
#find_package(rabbitmq-c 0.8.0)
#find_package(SimpleAmqpClient 0.5.3)
#find_package(hiredis 0.5.3)

# DAQ Libraries
set(daq_libs "daq_ims" "daq_daq" "daq_dsi")
foreach(x ${daq_libs})
    find_library(${x} name lib${x}.so HINTS "${DAQ_DIR}/x86/lib")
endforeach()

# Boost version specific libraries
set(boost_libs 
    "boost_log" 
    "boost_filesystem" 
    "boost_system" 
    "boost_thread"
    "boost_unit_test_framework"
)
foreach(x ${boost_libs})
    find_library(${x} name lib${x}.so.${BOOST_VERSION} HINTS "/usr/local/lib")
endforeach()

include(ExternalProject)
ExternalProject_Add(yaml-cpp
    URL "${IIP_PACKAGE_REPO}/yaml-cpp/yaml-cpp-0.5.3.tar.gz"
)

# =============================================================================
add_subdirectory("./src/core")
add_subdirectory("./src/forwarder")
add_subdirectory("./src/tests")

# =============================================================================
# Install directives

install(TARGETS lsst_iip_core lsst_iip_forwarder lsst_iip_tests iip_forwarder test_exe
    LIBRARY DESTINATION "dm_forwarder/lib"
    RUNTIME DESTINATION "dm_forwarder/bin"
)
install(FILES "${PROJECT_SOURCE_DIR}/etc/config/ForwarderCfg.yaml" DESTINATION "dm_forwarder/config")
install(FILES "${PROJECT_SOURCE_DIR}/bin/setup.env" DESTINATION "dm_forwarder/bin")
install(DIRECTORY "${PROJECT_SOURCE_DIR}/include" DESTINATION "dm_forwarder/include")
# =============================================================================
# Create RPM

set(CPACK_GENERATOR "RPM")
set(CPACK_PACKAGE_NAME "dm_forwarder")
set(CPACK_PACKAGE_VENDOR "Large Synoptic Survey Telescope")
set(CPACK_PACKAGE_SUMMARY "LSST Data Management Forwarder component for archiving and transferring fitsfile")
set(CPACK_PACKAGE_VERSION_MAJOR ${PROJECT_VERSION_MAJOR})
set(CPACK_PACKAGE_VERSION_MINOR ${PROJECT_VERSION_MINOR})
set(CPACK_PACKAGE_VERSION_PATCH ${PROJECT_VERSION_PATCH})
#set(CPACK_PACKAGE_INSTALL_DIRECTORY "helloworld")

set(CPACK_RPM_PACKAGE_DESCRIPTION 
    "Forwarder is part of Image Ingest and Processing Pipeline for LSST Data 
    Management System developed by team at National Center for SuperComputing 
    Applications(NCSA). Forwarder is the worker application that executes fitsfile 
    image assembly and transferring the files to Archive Data Facility.")
set(CPACK_RPM_PACKAGE_URL "www.lsst.org")
set(CPACK_RPM_PACKAGE_ARCHITECTURE "x86_64")
set(CPACK_RPM_PACKAGE_RELEASE 1.el7)
set(CPACK_RPM_PACKAGE_LICENSE "GPL")
set(CPACK_RPM_PACKAGE_GROUP "lsst-dm")
set(CPACK_RPM_PACKAGE_DESCRIPTION "www.lsst.org")
set(CPACK_RPM_PACKAGE_MAINTAINER "Htut Khine Htay Win <hwin16@illinois.edu>")
set(CPACK_RPM_PACKAGE_REQUIRES "which >= 2.20")
set(CPACK_RPM_PACKAGE_REQUIRES "librabbitmq >= 0.8.0")
set(CPACK_RPM_PACKAGE_REQUIRES "librabbitmq-devel >= 0.8.0")
set(CPACK_RPM_PACKAGE_REQUIRES "libcurl >= 7.29.0")
set(CPACK_RPM_PACKAGE_REQUIRES "libcurl-devel >= 7.29.0")
set(CPACK_RPM_PACKAGE_RELOCATABLE ON)
include(CPack)
