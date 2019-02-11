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
`$ yum install gcc rpm-build rpm-devel rpmlint make coreutils rpmdevtools`

# Install order
Certain spec files have dependencies on other spec files.
* l1-boost.spec
* l1-rabbitmq-c.spec
* l1-simpleAmqpClient.spec
* l1-yaml-cpp.spec
* l1-atArchiver.spec

# Install
`$ rpmdev-setuptree`
`$ rpmbuild --undefine=_disable_source_fetch -ba <spec-filename>.spec`
`$ sudo yum install -y <rpm-file-name>.rpm`

`rpmdev-setuptree` creates `~/rpmbuild` directory with sub directories for
putting SOURCES, RPMS and such.  
`rpmbuild` creates RPM files at `~/rpmbuild/RPMS/x86_64`.  
`yum` installs the RPM into the location specified in the spec file.

P.S. `disable_source_fetch` enables the user to download zip/tar.gz files from the
internet. By default, RPM blocks downloading untrusted code archives from the internet.

# Install python3-devel
Add EPEL to your repolist.
`yum install
https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm`

# License 
MIT

