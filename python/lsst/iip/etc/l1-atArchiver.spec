# check for python3
# check for lsst directory path
# setup start_up/services

%define lsstpath /opt/lsst

Name:	        lsst-atArchiver	
Version:        1.6	
Release:	1%{?dist}
Summary:        ATArchiver software package for Data Management Services	

Group:	        Applications/System	
License:        MIT	
URL:		http://www.ncsa.illinois.edu/enabling/data/lsst
Source0:        https://github.com/lsst/ctrl_iip/archive/develop.zip	

BuildRequires:  openssl-devel gcc make python36 python36-devel	
BuildRequires:  lsst-boost
BuildRequires:  lsst-simpleAmqpClient
BuildRequires:  lsst-rabbitmq-c
BuildRequires:  lsst-yaml-cpp

BuildArch:      x86_64

%description
ATArchiver software contains multiple sub packages - OCS Bridge, DMCS,
DMCS, atArchiver, Forwarder. This package implements end-to-end
architecture from receiving incoming messages from Observatory Control
System to archiving fits file data at the Archiver.

%prep
%setup -q -n ctrl_iip-develop

%build
#%%configure
# make %{?_smp_mflags}
/usr/local/bin/python3 -m compileall *.py

%install
# make install DESTDIR=%{buildroot}
# create bin, lib, include, config directories
#mkdir -p %{buildroot}/%{lsstpath}/bin
#mkdir -p %{buildroot}/%{lsstpath}/lib
#mkdir -p %{buildroot}/%{lsstpath}/include
#mkdir -p %{buildroot}/%{lsstpath}/config
#mkdir -p %{buildroot}/%{lsstpath}/share

# create executables for all python files
#for pyfile in $(ls *.pyc); do
#    echo $pyfile
#done

%files
%doc



%changelog

