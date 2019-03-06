# Description
Large Synoptic Survey Telescope(LSST) project entails that our deployment system
will be coupled with RPMS and Puppet. To accommodate the requirement, NCSA L1
Team publishes the following RPM Spec files. 
* l1-rabbitmq-c - RabbitMQ C Wrapper for OCS Bridge software
* l1-simpleAmqpClient - RabbitMQ C++ Wrapper for OCS Bridge software
* l1-yaml-cpp - C++ Wrapper for YAML
* l1-boost - Boost version 1.63.0 for Forwarder Logging
* l1-atArchiver - ATArchiver software package

Default install location is `/opt/lsst`.

# Prerequisites
* `$ yum install gcc rpm-build rpm-devel rpmlint make coreutils rpmdevtools`
* RPMS uses `/opt/lsst/dm-prompt/bin` directory to run the software. So, the
  directory has be have 777 permission by the unprivileged user defined below.
* RPMS assume certain unprivileged users for certain packages
    * ATArchiver - ATS
    * OCSBridge - OCS

# Install order
Certain spec files have dependencies on other spec files.
* l1-boost.spec
* l1-rabbitmq-c.spec
* l1-simpleAmqpClient.spec
* l1-yaml-cpp.spec
* l1-atArchiver.spec

# Install
`$ rpmdev-setuptree`
`$ QA_RPATHS=$[0x0002] rpmbuild --undefine=_disable_source_fetch -ba l1-atArchiver.spec`
`$ sudo yum install -y <rpm-file-name>.rpm`

`rpmdev-setuptree` creates `~/rpmbuild` directory with sub directories for
putting SOURCES, RPMS and such.  
`rpmbuild` creates RPM files at `~/rpmbuild/RPMS/x86_64`. QA_RPATHS is for
suppressing warning for rpath issue.  
`yum` installs the RPM into the location specified in the spec file.

P.S. `disable_source_fetch` enables the user to download zip/tar.gz files from the
internet. By default, RPM blocks downloading untrusted code archives from the internet.

# Install python3-devel
Add EPEL to your repolist.
`yum install
https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm`

# Postinstall 
Most of the RPM install systemd service files. So, it is recommended to run the
`systemctl daemon-reload` after installing the rpm.

# License 
MIT

