# check for python3
# check for lsst directory path
# setup start_up/services

%define lsstpath /opt/lsst/dm-prompt
%define gitbranch tickets/DM-17833
%define gitdash tickets-DM-17833

Name:	        lsst-atArchiver	
Version:        1.6	
Release:	1%{?dist}
Summary:        ATArchiver software package for Data Management Services	

Group:	        Applications/System	
License:        MIT	
URL:		http://www.ncsa.illinois.edu/enabling/data/lsst
Source0:        https://github.com/lsst/ctrl_iip/archive/%{gitbranch}.zip	

BuildRequires:  openssl-devel gcc make python36 python36-devel	
BuildRequires:  lsst-boost
BuildRequires:  lsst-simpleAmqpClient
BuildRequires:  lsst-rabbitmq-c
BuildRequires:  lsst-yaml-cpp

BuildArch:      x86_64

Prefix:         /opt/lsst

%description
ATArchiver software contains multiple sub packages - OCS Bridge, DMCS,
DMCS, atArchiver, Forwarder. This package implements end-to-end
architecture from receiving incoming messages from Observatory Control
System to archiving fits file data at the Archiver.

%prep
%setup -q -n ctrl_iip-%{gitdash}

%build
cd python/lsst/iip
make

%install
cd python/lsst/iip

# install python, ocsbridge executables
install -d %{buildroot}%{lsstpath}/bin %{buildroot}%{lsstpath}/include
install -m 755 -D *.py %{buildroot}%{lsstpath}/bin
install -m 755 -D ocs/include/* %{buildroot}%{lsstpath}/include

# install systemd scripts
install -d %{buildroot}etc/systemd/system
install -D start_up/l1d* %{buildroot}etc/systemd/system
install -D start_up/run* %{buildroot}%{lsstpath}/bin
systemctl daemon-reload

%files
%{lsstpath}/bin/*
%{lsstpath}/include/*

%doc


%changelog

