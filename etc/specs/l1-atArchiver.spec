%define lsstpath /opt/lsst/dm-prompt
%define gitbranch tickets/DM-18375
%define gitdash tickets-DM-18375
%define user ATS

Name:	        lsst-atArchiver	
Version:        1.6	
Release:	1%{?dist}
Summary:        ATArchiver software package for Data Management Services	

Group:	        Applications/System	
License:        MIT	
URL:		http://www.ncsa.illinois.edu/enabling/data/lsst
Source0:        https://github.com/lsst/ctrl_iip/archive/%{gitbranch}.zip	

BuildRequires:  python36 python36-devel	

BuildArch:      x86_64

%description
ATArchiver software manages the compute resources for Data Management Software
System to perform image processing.

%prep
%setup -q -n ctrl_iip-%{gitdash}

%build
make

%install
install -d %{buildroot}%{lsstpath}/bin %{buildroot}%{lsstpath}/python %{buildroot}%{lsstpath}/python/logs %{buildroot}%{lsstpath}/config
install -d %{buildroot}/etc/systemd/system

install -m 755 -D python/lsst/iip/*.py %{buildroot}%{lsstpath}/python
install -m 755 -D bin/CommandListener %{buildroot}%{lsstpath}/bin
install -m 755 -D bin/EventSubscriber %{buildroot}%{lsstpath}/bin
install -m 755 -D bin/AckSubscriber %{buildroot}%{lsstpath}/bin
install -m 755 -D bin/check_services.sh %{buildroot}%{lsstpath}/bin
install -m 755 -D bin/at_rmq_purge_queues.sh %{buildroot}%{lsstpath}/bin
install -m 755 -D etc/config/L1SystemCfg.yaml %{buildroot}%{lsstpath}/config
install -D etc/services/l1d-* %{buildroot}/etc/systemd/system

%files
%defattr(755, %{user}, %{user}, 755) 
%{lsstpath}/bin/*
%{lsstpath}/python/*
%{lsstpath}/config/*
%attr(-, root, root) /etc/systemd/system/l1d-*

%doc

%changelog
