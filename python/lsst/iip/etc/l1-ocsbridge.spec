%define lsstpath /opt/lsst/dm-prompt
%define gitbranch tickets/DM-17833
%define gitdash tickets-DM-17833

Name:	        lsst-ocsbridge
Version:        1.6	
Release:	1%{?dist}
Summary:        OCS Bridge software package for Data Management Services	

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
OCSBridge software is the communicator between OCS(Observatory Control System)
and DMCS(Data Management System). OCSBridge consists of three components -
CommandListener, EventSubscriber and AckSubscriber. CommandListener listens to
SAL commands from OCS and translates them to Rabbitmq messages. EventSubscriber
listens to events from OCS and translates them to Rabbitmq messages.
AckSubscriber listens to DMCS Rabbitmq messages and acks back to OCS. 

%prep
%setup -q -n ctrl_iip-%{gitdash}

%build
cd python/lsst/iip/ocs/src
make

%install
cd python/lsst/iip

# need dds libraries/dds rpm to fix OCS build issue
install -d %{buildroot}%{lsstpath}/bin %{buildroot}%{lsstpath}/include
install -d %{buildroot}/etc/systemd/system
install -m 755 -D ocs/include/* %{buildroot}%{lsstpath}/include
install -m 755 -D ocs/bin/* %{buildroot}%{lsstpath}/bin
install -D start_up/l1d-AckSubscriber %{buildroot}/etc/systemd/system
install -D start_up/l1d-CommandListener %{buildroot}/etc/systemd/system
install -D start_up/l1d-EventSubscriber %{buildroot}/etc/systemd/system
install -D start_up/run* %{buildroot}%{lsstpath}/bin

%files
%{lsstpath}/bin/*
%{lsstpath}/include/*
/etc/systemd/system/l1*

%doc


%changelog

